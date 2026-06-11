import React, { useEffect, useState, useCallback, useRef } from 'react';
import { Helmet } from 'react-helmet-async';
import { useVirtualizer } from '@tanstack/react-virtual';
import { fetchGames } from '../api/gameService';
import type { Game } from '../types/game';
import { Link } from 'react-router-dom';

export const ComparisonPage: React.FC = () => {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const parentRef = useRef<HTMLDivElement>(null);

  const loadGames = useCallback(async (searchQuery: string) => {
    setLoading(true);
    const res = await fetchGames(searchQuery);
    setGames(res.data);
    setLoading(false);
  }, []);

  useEffect(() => { loadGames(query); }, [query, loadGames]);

  const virtualizer = useVirtualizer({
    count: games.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 110,
    overscan: 5,
  });

  return (
    <div className='comparison-container'>
      <Helmet>
        <title>ボドゲのミカタ | 最強のボードゲーム検索・比較ツール</title>
        <meta name='description' content='9万件以上のボードゲームデータから、あなたにぴったりの1本を見つける。重さ、人数、プレイ時間で瞬時に比較検索。' />
      </Helmet>
      
      <header>
        <h1>ボドゲのミカタ</h1>
        <p>90,000点を超えるBoardGameGeekデータベースから、あなたにぴったりのボードゲームを検索・比較できます。</p>
      </header>

      <div className='controls-card'>
        <div className='search-wrapper'>
          <svg className="search-icon" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input 
            className='search-input'
            placeholder='ゲームのタイトルや説明から検索する...' 
            value={query} 
            onChange={e => setQuery(e.target.value)} 
          />
        </div>
      </div>

      {loading ? (
        <div className='loader-wrapper'>
          <div className='loader-spinner'></div>
          <p>データを読み込んでいます...</p>
        </div>
      ) : (
        <div ref={parentRef} style={{ height: '700px', overflow: 'auto', paddingRight: '0.5rem' }}>
          <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative', width: '100%' }}>
            {virtualizer.getVirtualItems().map(virtualRow => {
              const game = games[virtualRow.index];
              if (!game) return null;
              
              // Fallback image URL
              const imgUrl = game.image_url 
                ? (game.image_url.startsWith('//') ? 'https:' + game.image_url : game.image_url)
                : 'https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?auto=format&fit=crop&q=80&w=200';

              const mechanics = game.structured_data?.mechanics || [];

              return (
                <Link
                  to={`/game/${game.slug}`}
                  key={virtualRow.key}
                  className='game-card'
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: `95px`,
                    transform: `translateY(${virtualRow.start}px)`,
                    margin: '5px 0'
                  }}
                >
                  <div className='game-image-wrapper'>
                    <img className='game-image' src={imgUrl} alt={game.title} loading="lazy" />
                  </div>
                  
                  <div className='game-info'>
                    <div className='game-title'>{game.title_ja || game.title}</div>
                    
                    <div className='game-meta'>
                      <span className='meta-badge players'>👤 {game.min_players}-{game.max_players}人</span>
                      <span className='meta-badge time'>⏱️ {game.play_time}分</span>
                      <span className='meta-badge year'>📅 {game.published_year}年</span>
                    </div>

                    <div className='mechanics-tags'>
                      {mechanics.slice(0, 3).map((m: string, idx: number) => (
                        <span key={idx} className='mechanic-tag'>{m}</span>
                      ))}
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
