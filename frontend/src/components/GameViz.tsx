import React from 'react';

interface GameVizProps {
  weight: number;
  depth: number;
  players: number;
  strategy: number;
}

export const GameViz: React.FC<GameVizProps> = ({ weight, depth, players, strategy }) => {
  const size = 100;
  const center = size / 2;
  const radius = 40;
  const normalized = [weight / 5, depth / 5, players / 5, strategy / 5];
  const points = normalized.map((val, i) => {
    const angle = i * (Math.PI / 2);
    return {
      x: center + Math.cos(angle) * radius * val,
      y: center + Math.sin(angle) * radius * val,
    };
  });
  const pathData = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
  return (
    <svg viewBox="0 0 100 100" className="w-24 h-24">
      <polygon points="50,10 90,50 50,90 10,50" fill="none" stroke="#e5e7eb" strokeWidth="1" />
      <polygon points={pathData} fill="rgba(59, 130, 246, 0.5)" stroke="#3b82f6" strokeWidth="2" />
    </svg>
  );
};
