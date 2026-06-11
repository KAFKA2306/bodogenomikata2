import React, { useState } from 'react';
import { postReview } from '../api/gameService';

export const ReviewForm: React.FC<{ slug: string }> = ({ slug }) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await postReview(slug, rating, comment);
    alert('Review submitted!');
    setComment('');
  };

  return (
    <form onSubmit={handleSubmit} className="review-form">
      <h3>Review this game</h3>
      <input type="number" min="1" max="5" value={rating} onChange={e => setRating(Number(e.target.value))} />
      <textarea value={comment} onChange={e => setComment(e.target.value)} placeholder="Your thoughts..." />
      <button type="submit">Submit</button>
    </form>
  );
};
