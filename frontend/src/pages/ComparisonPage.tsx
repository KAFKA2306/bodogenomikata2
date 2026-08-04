import React, { useEffect, useState, useCallback } from 'react';
import { Helmet } from 'react-helmet-async';
import { Link, useSearchParams } from 'react-router-dom';
import { fetchGames } from '../api/gameService';
import type { Game } from '../types/game';

export const ComparisonPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const query = searchParams.get('q') || '';

  const loadGames = useCallback(async (searchQuery: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchGames(searchQuery);
      setGames(res.data);
    } catch {
      setError('バックエンドサーバーに接続できませんでした。APIサーバーが稼働中か確認してください。');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => loadGames(query), 250);
    return () => window.clearTimeout(timer);
  }, [query, loadGames]);

  const updateQuery = (value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set('q', value); else next.delete('q');
    setSearchParams(next, { replace: true });
  };

  return (
    <div className='comparison-container'>
      <Helmet>
        <html lang="ja" />
        <title>作品・創作を調べる | ボドゲのミカタ</title>
        <meta name="description" content="作品、人数、時間、メカニクス、公開レビューを調べるモード。卓上の裁定回答とは分離しています。" />
      </Helmet>
      <header>
        <p className="workflow-eyebrow">RESEARCH MODE</p>
        <h1>作品・創作を調べる</h1>
        <p>作品検索、メカニクス、公開情報、レビューを扱います。プレイ中の裁定回答とは別のモードです。</p>
      </header>

      <section className='controls-card' role="search" aria-label="作品検索">
        <label className='search-wrapper' htmlFor="research-query">
          <svg className='search-icon' width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            id="research-query"
            type="search"
            className='search-input'
            placeholder='ゲームタイトルで検索...'
            value={query}
            onChange={event => updateQuery(event.target.value)}
          />
        </label>
        <p className="results-meta" role="status">{loading ? '検索中' : `${games.length}件を表示`} · 条件はURLに保存されます。</p>
      </section>

      {loading ? (
        <div className='loader-wrapper' role="status"><div className='loader-spinner'></div><p>ボードゲームを検索中...</p></div>
      ) : error ? (
        <div className="workflow-error" role="alert">{error}</div>
      ) : games.length === 0 ? (
        <div className="empty-state"><h2>条件に一致する作品がありません</h2><p>作品名を変更してください。</p><button type="button" className="workflow-action workflow-button" onClick={() => updateQuery('')}>全作品を表示</button></div>
      ) : (
        <section className='games-grid' aria-label="作品一覧">
          {games.map(game => {
            const imgUrl = game.image_url
              ? (game.image_url.startsWith('//') ? `https:${game.image_url}` : game.image_url)
              : 'https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?auto=format&fit=crop&q=80&w=200';
            const mechanics = game.structured_data?.mechanics?.slice(0, 3) || [];
            return (
              <Link to={`/game/${game.slug}`} key={game.id} className='game-card'>
                <div className='game-image-wrapper'><img className='game-image' src={imgUrl} alt={`${game.title_ja || game.title}の作品画像`} width="400" height="300" loading="lazy" /></div>
                <div className='game-info'>
                  <h3 className='game-title'>{game.title_ja || game.title}</h3>
                  <div className='game-meta'><span className='meta-badge players'>👤 {game.min_players}-{game.max_players}人</span><span className='meta-badge time'>⏱️ {game.play_time}分</span><span className='meta-badge year'>📅 {game.published_year}年</span></div>
                  {mechanics.length > 0 && <div className='mechanics-tags'>{mechanics.map((mechanic, index) => <span key={index} className='mechanic-tag'>{mechanic}</span>)}</div>}
                </div>
              </Link>
            );
          })}
        </section>
      )}
    </div>
  );
};
