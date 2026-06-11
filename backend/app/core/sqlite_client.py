import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def get_db_path() -> Path:
    db_path_env = os.getenv("DATABASE_URL")
    if db_path_env:
        return Path(db_path_env).resolve()
    return Path(__file__).resolve().parent.parent.parent / "games.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    from app.core.init_sqlite import init_database as _init

    _init(str(get_db_path()))


def _parse_game_row(row: Any) -> dict[str, Any]:
    game = dict(row)
    # Crash-Driven: Assume JSON strings are always valid and present if keys exist
    for field in ["metadata", "infographics", "structured_data"]:
        if game.get(field):
            game[field] = json.loads(game[field])
    return game


def upsert_game(game_data: dict[str, Any]) -> dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    slug = game_data["slug"]

    data = game_data.copy()
    # Ensure success path by providing defaults for optional JSON fields if they are the target of serialization
    for field in ["metadata", "infographics", "structured_data"]:
        val = data.get(field) or {}
        data[field] = json.dumps(val, ensure_ascii=False)

    now = datetime.now(timezone.utc).isoformat()
    data["updated_at"] = now

    cursor.execute("PRAGMA table_info(games)")
    columns = [col[1] for col in cursor.fetchall()]
    valid_data = {k: v for k, v in data.items() if k in columns}

    cursor.execute("SELECT id FROM games WHERE slug = ?", (slug,))
    if cursor.fetchone():
        fields = [f"{k} = ?" for k in valid_data if k != "slug"]
        values = [valid_data[k] for k in valid_data if k != "slug"] + [slug]
        cursor.execute(f"UPDATE games SET {', '.join(fields)} WHERE slug = ?", values)
    else:
        valid_data["created_at"] = now
        keys = list(valid_data.keys())
        cursor.execute(
            f"INSERT INTO games ({', '.join(keys)}) VALUES ({', '.join(['?'] * len(keys))})", list(valid_data.values())
        )

    conn.commit()
    cursor.execute("SELECT * FROM games WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    conn.close()
    return _parse_game_row(row)


def get_game_by_slug(slug: str) -> dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE games SET view_count = view_count + 1, updated_at = ? WHERE slug = ?",
        (datetime.now(timezone.utc).isoformat(), slug),
    )
    conn.commit()
    cursor.execute("SELECT * FROM games WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    conn.close()
    return _parse_game_row(row)


def list_games(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games ORDER BY updated_at DESC LIMIT ? OFFSET ?", (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return [_parse_game_row(row) for row in rows]


def delete_game(slug: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM games WHERE slug = ?", (slug,))
    conn.commit()
    conn.close()


def get_total_games() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM games")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_game_credits(slug: str) -> dict[str, list[dict[str, Any]]]:
    conn = get_connection()
    cursor = conn.cursor()

    # Designers
    cursor.execute(
        """
        SELECT d.slug, d.name, d.name_ja, d.name_en, d.bgg_id
        FROM designers d
        JOIN game_designers gd ON d.slug = gd.designer_slug
        WHERE gd.game_slug = ?
        """,
        (slug,)
    )
    designers = [dict(r) for r in cursor.fetchall()]

    # Publishers
    cursor.execute(
        """
        SELECT p.slug, p.name, p.name_ja, p.name_en, p.bgg_id
        FROM publishers p
        JOIN game_publishers gp ON p.slug = gp.publisher_slug
        WHERE gp.game_slug = ?
        """,
        (slug,)
    )
    publishers = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {"designers": designers, "publishers": publishers}


def get_game_expansions(slug: str) -> dict[str, list[dict[str, Any]]]:
    conn = get_connection()
    cursor = conn.cursor()

    # Expansions (children)
    cursor.execute(
        """
        SELECT g.slug, g.title, g.title_ja, g.title_en, g.image_url, g.published_year
        FROM games g
        JOIN game_relationships gr ON g.slug = gr.child_slug
        WHERE gr.parent_slug = ? AND gr.relation_type = 'expansion'
        """,
        (slug,)
    )
    expansions = [dict(r) for r in cursor.fetchall()]

    # Parents (base games)
    cursor.execute(
        """
        SELECT g.slug, g.title, g.title_ja, g.title_en, g.image_url, g.published_year
        FROM games g
        JOIN game_relationships gr ON g.slug = gr.parent_slug
        WHERE gr.child_slug = ? AND gr.relation_type = 'expansion'
        """,
        (slug,)
    )
    parents = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {"expansions": expansions, "parents": parents}


def upsert_game_credits_and_relations(
    game_slug: str,
    designers: list[dict[str, Any]],
    publishers: list[dict[str, Any]],
    expansions: list[dict[str, Any]],
    expands: list[dict[str, Any]]
) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Insert/upsert designers
    for d in designers:
        d_slug = d["slug"]
        cursor.execute(
            """
            INSERT INTO designers (slug, name, bgg_id)
            VALUES (?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET name=excluded.name, bgg_id=excluded.bgg_id
            """,
            (d_slug, d["name"], d.get("bgg_id"))
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO game_designers (game_slug, designer_slug)
            VALUES (?, ?)
            """,
            (game_slug, d_slug)
        )

    # 2. Insert/upsert publishers
    for p in publishers:
        p_slug = p["slug"]
        cursor.execute(
            """
            INSERT INTO publishers (slug, name, bgg_id)
            VALUES (?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET name=excluded.name, bgg_id=excluded.bgg_id
            """,
            (p_slug, p["name"], p.get("bgg_id"))
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO game_publishers (game_slug, publisher_slug)
            VALUES (?, ?)
            """,
            (game_slug, p_slug)
        )

    # 3. Handle game relationships
    for child in expansions:
        c_slug = child["slug"]
        cursor.execute(
            """
            INSERT OR IGNORE INTO games (slug, title, bgg_id, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (c_slug, child["name"], child.get("bgg_id"))
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO game_relationships (parent_slug, child_slug, relation_type)
            VALUES (?, ?, 'expansion')
            """,
            (game_slug, c_slug)
        )

    for parent in expands:
        p_slug = parent["slug"]
        cursor.execute(
            """
            INSERT OR IGNORE INTO games (slug, title, bgg_id, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (p_slug, parent["name"], parent.get("bgg_id"))
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO game_relationships (parent_slug, child_slug, relation_type)
            VALUES (?, ?, 'expansion')
            """,
            (p_slug, game_slug)
        )

    conn.commit()
    conn.close()


def search_games(
    query: str | None = None,
    min_players: int | None = None,
    max_players: int | None = None,
    play_time: int | None = None,
    mechanics: list[str] | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT DISTINCT * FROM games WHERE 1=1"
    params = []

    if query:
        sql += " AND (title LIKE ? OR title_ja LIKE ? OR title_en LIKE ? OR description LIKE ?)"
        like_query = f"%{query}%"
        params.extend([like_query, like_query, like_query, like_query])

    if min_players is not None:
        sql += " AND min_players >= ?"
        params.append(min_players)

    if max_players is not None:
        sql += " AND max_players <= ?"
        params.append(max_players)

    if play_time is not None:
        sql += " AND play_time <= ?"
        params.append(play_time)

    if mechanics:
        for mech in mechanics:
            sql += " AND EXISTS (SELECT 1 FROM json_each(structured_data, '$.mechanics') WHERE value = ?)"
            params.append(mech)

    sql += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [_parse_game_row(row) for row in rows]


def get_games_modified_since(last_sync_at: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if last_sync_at:
        cursor.execute("SELECT * FROM games WHERE updated_at > ? ORDER BY updated_at DESC", (last_sync_at,))
    else:
        cursor.execute("SELECT * FROM games ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [_parse_game_row(row) for row in rows]


def autocomplete_suggestions(query: str, limit: int = 10) -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    SELECT slug, title, title_ja, title_en
    FROM games
    WHERE title LIKE ? OR title_ja LIKE ? OR title_en LIKE ?
    LIMIT ?
    """
    prefix_param = f"{query}%"
    cursor.execute(sql, (prefix_param, prefix_param, prefix_param, limit))
    results = [dict(row) for row in cursor.fetchall()]

    if len(results) < limit:
        partial_param = f"%{query}%"
        if results:
            placeholders = ", ".join("?" for _ in results)
            cursor.execute(
                f"""
                SELECT slug, title, title_ja, title_en
                FROM games
                WHERE (title LIKE ? OR title_ja LIKE ? OR title_en LIKE ?)
                  AND slug NOT IN ({placeholders})
                LIMIT ?
                """,
                [partial_param, partial_param, partial_param] + [r["slug"] for r in results] + [limit - len(results)],
            )
        else:
            cursor.execute(
                """
                SELECT slug, title, title_ja, title_en
                FROM games
                WHERE title LIKE ? OR title_ja LIKE ? OR title_en LIKE ?
                LIMIT ?
                """,
                [partial_param, partial_param, partial_param, limit],
            )
        results.extend([dict(row) for row in cursor.fetchall()])
    conn.close()
    return results


def get_game_skeletons() -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, slug, title, title_ja, title_en, image_url, min_players, max_players, play_time, updated_at FROM games ORDER BY updated_at DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_user_review(game_slug: str) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_reviews WHERE game_slug = ?", (game_slug,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_user_review(game_slug: str, rating: float, comment: str | None) -> dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        INSERT INTO user_reviews (game_slug, rating, comment, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(game_slug) DO UPDATE SET
            rating = excluded.rating,
            comment = excluded.comment,
            updated_at = excluded.updated_at
        """,
        (game_slug, rating, comment, now, now),
    )
    conn.commit()
    cursor.execute("SELECT * FROM user_reviews WHERE game_slug = ?", (game_slug,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def delete_user_review(game_slug: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_reviews WHERE game_slug = ?", (game_slug,))
    conn.commit()
    conn.close()


def get_user_collection(game_slug: str) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_collections WHERE game_slug = ?", (game_slug,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_user_collection(game_slug: str, status: str) -> dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        INSERT INTO user_collections (game_slug, status, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(game_slug) DO UPDATE SET
            status = excluded.status,
            updated_at = excluded.updated_at
        """,
        (game_slug, status, now, now),
    )
    conn.commit()
    cursor.execute("SELECT * FROM user_collections WHERE game_slug = ?", (game_slug,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def delete_user_collection(game_slug: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_collections WHERE game_slug = ?", (game_slug,))
    conn.commit()
    conn.close()


def save_artworks(game_slug: str, artworks: list[dict]) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM game_artworks WHERE game_slug = ?", (game_slug,))
    for art in artworks:
        cursor.execute(
            "INSERT INTO game_artworks (game_slug, image_url, title) VALUES (?, ?, ?)",
            (game_slug, art["image_url"], art.get("title")),
        )
    conn.commit()
    conn.close()


def get_artworks(game_slug: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM game_artworks WHERE game_slug = ?", (game_slug,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_videos(game_slug: str, videos: list[dict]) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    for vid in videos:
        cursor.execute(
            """
            INSERT INTO game_videos (game_slug, video_id, title, url, thumbnail_url, duration, views_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(game_slug, video_id) DO UPDATE SET
                title = excluded.title,
                url = excluded.url,
                thumbnail_url = excluded.thumbnail_url,
                duration = excluded.duration,
                views_count = excluded.views_count,
                updated_at = excluded.updated_at
            """,
            (
                game_slug,
                vid["video_id"],
                vid["title"],
                vid["url"],
                vid.get("thumbnail_url"),
                vid.get("duration"),
                vid.get("views_count", 0),
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
    conn.commit()
    conn.close()


def get_videos(game_slug: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM game_videos WHERE game_slug = ? ORDER BY id ASC", (game_slug,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
