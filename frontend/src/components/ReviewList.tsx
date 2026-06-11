import React, { useEffect, useState } from 'react';
import { fetchReviews } from '../api/gameService';

export const ReviewList: React.FC<{ slug: string }> = ({ slug }) => {
  const [reviews, setReviews] = useState<{ rating: number, comment: string }[]>([]);

  useEffect(() => {
    fetchReviews(slug).then(res => setReviews(res.data));
  }, [slug]);

  return (
    <div className='review-list'>
      <h3>Community Reviews</h3>
      {reviews.map((r, i) => (
        <div key={i} className='review-item'>
          <p>Rating: {r.rating}/5</p>
          <p>{r.comment}</p>
        </div>
      ))}
    </div>
  );
};
