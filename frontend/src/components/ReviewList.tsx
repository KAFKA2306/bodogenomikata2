import React, { useEffect, useState } from 'react';
import { fetchReviews } from '../api/gameService';

export const ReviewList: React.FC<{ slug: string }> = ({ slug }) => {
  const [reviews, setReviews] = useState<{ rating: number, comment: string }[]>([]);

  useEffect(() => {
    fetchReviews(slug).then(res => setReviews(res.data));
  }, [slug]);

  return (
    <div className='review-list'>
      <h3>みんなのレビュー</h3>
      {reviews.length === 0 ? (
        <p className="no-reviews">まだレビューはありません。最初のレビューを投稿してみましょう！</p>
      ) : (
        reviews.map((r, i) => (
          <div key={i} className='review-item'>
            <div className='review-item-header'>
              <span className='review-rating-stars'>{'★'.repeat(r.rating)}{'☆'.repeat(5 - r.rating)}</span>
              <span className='review-rating-num'>{r.rating}/5</span>
            </div>
            <p className='review-comment'>{r.comment}</p>
          </div>
        ))
      )}
    </div>
  );
};

