import React, { useEffect, useState, useCallback } from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import { fetchGames } from '../api/gameService';
import type { Game } from '../types/game';

export const ComparisonPage: React.FC = () => {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');

  const loadGames = useCallback(async (searchQuery: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchGames(searchQuery);
      setGames(res.data);
    } catch (err) {
      setError('バックエンドサーバーに接続できませんでした。APIサーバーが稼働中か確認してください。');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadGames(query); }, [query, loadGames]);

  return (
    <div className='comparison-container'>
      <Helmet>
        <title>ボドゲのミカタ | 最強のボードゲーム検索・比較ツール</title>
      </Helmet>
      
      <header>
        <h1>ボドゲのミカタ</h1>
        <p>AI要約やインスト、みんなのレビューが見られるボードゲームポータルサイト</p>
      </header>

      <div className='controls-card'>
        <div className='search-wrapper'>
          <svg className='search-icon' width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input 
            className='search-input'
            placeholder='ゲームタイトルで検索...' 
            value={query} 
            onChange={e => setQuery(e.target.value)} 
          />
        </div>
      </div>

      {loading ? (
        <div className='loader-wrapper'>
          <div className='loader-spinner'></div>
          <p>ボードゲームを検索中...</p>
        </div>
      ) : error ? (
        <div style={{color: '#EF4444', textAlign: 'center', padding: '2rem', fontWeight: 600}}>{error}</div>
      ) : (
        <div className='games-grid'>
          {games.map(game => {
            const imgUrl = game.image_url 
              ? (game.image_url.startsWith('//') ? 'https:' + game.image_url : game.image_url)
              : 'https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?auto=format&fit=crop&q=80&w=200';
            const mechanics = game.structured_data?.mechanics?.slice(0, 3) || [];
            
            return (
              <Link to={`/game/${game.slug}`} key={game.id} className='game-card'>
                <div className='game-image-wrapper'>
                  <img className='game-image' src={imgUrl} alt={game.title} />
                </div>
                <div className='game-info'>
                  <h3 className='game-title'>{game.title_ja || game.title}</h3>
                  <div className='game-meta'>
                    <span className='meta-badge players'>👤 {game.min_players}-{game.max_players}人</span>
                    <span className='meta-badge time'>⏱️ {game.play_time}分</span>
                    <span className='meta-badge year'>📅 {game.published_year}年</span>
                  </div>
                  {mechanics.length > 0 && (
                    <div className='mechanics-tags'>
                      {mechanics.map((m, idx) => (
                        <span key={idx} className='mechanic-tag'>{m}</span>
                      ))}
                    </div>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
};

