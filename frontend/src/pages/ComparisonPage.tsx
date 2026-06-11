import React, { useEffect, useState, useCallback } from 'react';
import { fetchGames } from '../api/gameService';
import { Game } from '../types/game';

export const ComparisonPage: React.FC = () => {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');

  const loadGames = useCallback(async (searchQuery: string) => {
    setLoading(true);
    const res = await fetchGames(searchQuery);
    setGames(res.data);
    setLoading(false);
  }, []);

  useEffect(() => { loadGames(query); }, [query, loadGames]);

  return (
    <div className='comparison-container'>
      <h1>Board Game Comparison</h1>
      <div className='controls'>
        <input placeholder='Search by title...' value={query} onChange={e => setQuery(e.target.value)} />
      </div>
      {loading ? <div>Loading...</div> : (
      <table className='comparison-table'>
        <thead><tr><th>Title</th><th>Year</th><th>Players</th></tr></thead>
        <tbody>{games.map(game => (<tr key={game.id}><td>{game.title}</td><td>{game.published_year}</td><td>{game.min_players}-{game.max_players}</td></tr>))}</tbody>
      </table>
      )}
    </div>
  );
};
