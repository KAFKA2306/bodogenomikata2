import React, { useEffect, useState, useCallback, useRef } from 'react';
import { Helmet } from 'react-helmet-async';
import { useVirtualizer } from '@tanstack/react-virtual';
import { fetchGames } from '../api/gameService';
import type { Game } from '../types/game';

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
    estimateSize: () => 35,
    overscan: 5,
  });

  return (
    <div className='comparison-container'>
      <Helmet>
        <title>ボドゲのミカタ | 最強のボードゲーム検索・比較ツール</title>
        <meta name='description' content='9万件以上のボードゲームデータから、あなたにぴったりの1本を見つける。重さ、人数、プレイ時間で瞬時に比較検索。' />
      </Helmet>
      <h1>ボドゲのミカタ</h1>
      <div className='controls'>
        <input placeholder='Search by title...' value={query} onChange={e => setQuery(e.target.value)} />
      </div>
      {loading ? <div>Loading...</div> : (
        <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
          <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
            {virtualizer.getVirtualItems().map(virtualRow => {
              const game = games[virtualRow.index];
              return (
                <div
                  key={virtualRow.key}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: `${virtualRow.size}px`,
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                >
                  {game.title} ({game.published_year}) - {game.min_players}-{game.max_players}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
