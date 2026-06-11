import React, { useState } from 'react';
import { postReview } from '../api/gameService';

export const ReviewForm: React.FC<{ slug: string; onSubmitted?: () => void }> = ({ slug, onSubmitted }) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await postReview(slug, rating, comment);
    setComment('');
    if (onSubmitted) {
      onSubmitted();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="review-form">
      <h3>このゲームを評価する</h3>
      <div className="form-group-rating">
        <label>評価 (1-5):</label>
        <input 
          type="number" 
          min="1" 
          max="5" 
          value={rating} 
          onChange={e => setRating(Number(e.target.value))} 
          className="rating-input"
        />
      </div>
      <textarea 
        value={comment} 
        onChange={e => setComment(e.target.value)} 
        placeholder="ゲームの感想やレビューを書いてください..." 
        className="review-textarea"
        required
      />
      <button type="submit" className="submit-button">レビューを投稿</button>
    </form>
  );
};

