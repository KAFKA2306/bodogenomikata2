import React, { useEffect, useState, useCallback } from 'react';
import { Helmet } from 'react-helmet-async';
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
      <h1>ボドゲのミカタ</h1>
      <div className='controls'>
        <input placeholder='Search by title...' value={query} onChange={e => setQuery(e.target.value)} />
      </div>
      {loading ? <div>Loading...</div> :
       error ? <div style={{color: 'red'}}>{error}</div> : (
        <table className='comparison-table'>
          <thead><tr><th>Title</th><th>Year</th><th>Players</th></tr></thead>
          <tbody>{games.map(game => (<tr key={game.id}><td>{game.title}</td><td>{game.published_year}</td><td>{game.min_players}-{game.max_players}</td></tr>))}</tbody>
        </table>
      )}
    </div>
  );
};
