import sqlite3


def init_database(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create games table if not exists
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            title_ja TEXT,
            title_en TEXT,
            bgg_id INTEGER UNIQUE,
            summary TEXT,
            description TEXT,
            rules_summary TEXT,
            end_game_summary TEXT,
            rules_confidence REAL DEFAULT 0.5,
            setup_confidence REAL DEFAULT 0.5,
            gameplay_confidence REAL DEFAULT 0.5,
            end_game_confidence REAL DEFAULT 0.5,
            source_url TEXT,
            image_url TEXT,
            min_players INTEGER,
            max_players INTEGER,
            play_time INTEGER,
            min_age INTEGER,
            published_year INTEGER,
            is_official INTEGER DEFAULT 0,
            metadata TEXT,
            structured_data TEXT DEFAULT '{}',
            infographics TEXT DEFAULT '{}',
            view_count INTEGER DEFAULT 0,
            search_count INTEGER DEFAULT 0,
            data_version INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Category 1: Designers table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS designers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            name_ja TEXT,
            name_en TEXT,
            bgg_id INTEGER UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Category 1: Publishers table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS publishers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            name_ja TEXT,
            name_en TEXT,
            bgg_id INTEGER UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Category 1: Game Designers relation table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS game_designers (
            game_slug TEXT NOT NULL,
            designer_slug TEXT NOT NULL,
            PRIMARY KEY (game_slug, designer_slug),
            FOREIGN KEY (game_slug) REFERENCES games (slug) ON DELETE CASCADE,
            FOREIGN KEY (designer_slug) REFERENCES designers (slug) ON DELETE CASCADE
        )
        """
    )

    # Category 1: Game Publishers relation table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS game_publishers (
            game_slug TEXT NOT NULL,
            publisher_slug TEXT NOT NULL,
            PRIMARY KEY (game_slug, publisher_slug),
            FOREIGN KEY (game_slug) REFERENCES games (slug) ON DELETE CASCADE,
            FOREIGN KEY (publisher_slug) REFERENCES publishers (slug) ON DELETE CASCADE
        )
        """
    )

    # Category 1: Game Relationships (parent_slug, child_slug, relation_type)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS game_relationships (
            parent_slug TEXT NOT NULL,
            child_slug TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            PRIMARY KEY (parent_slug, child_slug, relation_type),
            FOREIGN KEY (parent_slug) REFERENCES games (slug) ON DELETE CASCADE,
            FOREIGN KEY (child_slug) REFERENCES games (slug) ON DELETE CASCADE
        )
        """
    )

    # Category 4: User Reviews table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_reviews (
            game_slug TEXT,
            user_id TEXT,
            rating REAL NOT NULL CHECK(rating >= 1.0 AND rating <= 10.0),
            comment TEXT,
            verified_purchase INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(game_slug, user_id),
            FOREIGN KEY(game_slug) REFERENCES games(slug) ON DELETE CASCADE
        )
        """
    )

    # Category 4: User Collections table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_collections (
            game_slug TEXT PRIMARY KEY,
            status TEXT NOT NULL CHECK(status IN ('owned', 'wishlist', 'played')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(game_slug) REFERENCES games(slug) ON DELETE CASCADE
        )
        """
    )

    # Category 5: Game Artworks table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS game_artworks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_slug TEXT NOT NULL,
            image_url TEXT NOT NULL,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(game_slug) REFERENCES games(slug) ON DELETE CASCADE
        )
        """
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_artworks_game_slug ON game_artworks(game_slug)")

    # Category 5: Game Videos table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS game_videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_slug TEXT NOT NULL,
            video_id TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            thumbnail_url TEXT,
            duration TEXT,
            views_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(game_slug, video_id),
            FOREIGN KEY(game_slug) REFERENCES games(slug) ON DELETE CASCADE
        )
        """
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_videos_game_slug ON game_videos(game_slug)")

    # Migrate existing tables to add new columns if they don't exist
    cursor.execute("PRAGMA table_info(games)")
    columns = [col[1] for col in cursor.fetchall()]

    additional_columns = [
        ("title_ja", "TEXT"),
        ("title_en", "TEXT"),
        ("bgg_id", "INTEGER"),
        ("summary", "TEXT"),
        ("end_game_summary", "TEXT"),
        ("rules_confidence", "REAL DEFAULT 0.5"),
        ("setup_confidence", "REAL DEFAULT 0.5"),
        ("gameplay_confidence", "REAL DEFAULT 0.5"),
        ("end_game_confidence", "REAL DEFAULT 0.5"),
        ("source_url", "TEXT"),
        ("image_url", "TEXT"),
        ("min_players", "INTEGER"),
        ("max_players", "INTEGER"),
        ("play_time", "INTEGER"),
        ("min_age", "INTEGER"),
        ("published_year", "INTEGER"),
        ("is_official", "INTEGER DEFAULT 0"),
        ("search_count", "INTEGER DEFAULT 0"),
        ("data_version", "INTEGER DEFAULT 1"),
        ("rules_content", "TEXT"),
        ("structured_data", "TEXT DEFAULT '{}'"),
        ("infographics", "TEXT DEFAULT '{}'"),
    ]

    for col_name, col_def in additional_columns:
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE games ADD COLUMN {col_name} {col_def}")

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_slug ON games(slug)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_title ON games(title)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_min_players ON games(min_players)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_max_players ON games(max_players)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_play_time ON games(play_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_view_count ON games(view_count)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_created_at ON games(created_at)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_games_bgg_id ON games(bgg_id)")

    conn.commit()
    conn.close()
