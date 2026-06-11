import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient } from '../api/client';
import { GameViz } from '../components/GameViz';
import { ReviewForm } from "../components/ReviewForm";
import type { Game } from '../types/game';

export const GameDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [game, setGame] = useState<Game | null>(null);

  useEffect(() => {
    apiClient.get(`/games/${slug}`).then(res => setGame(res.data.data));
  }, [slug]);

  if (!game) return <div>Loading...</div>;

  return (
    <div className='comparison-container'>
      <h1>{game.title}</h1>
      <div style={{ display: 'flex', gap: '2rem' }}>
        <div>
          <p>{game.description}</p>
        </div>
        <GameViz weight={4} depth={4} players={3} strategy={5} />
<ReviewForm slug={slug!} />
      </div>
    </div>
  );
};
