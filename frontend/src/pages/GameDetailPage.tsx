import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { apiClient } from '../api/client';
import { ReviewForm } from "../components/ReviewForm";
import { ReviewList } from "../components/ReviewList";
import type { Game } from '../types/game';

export const GameDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [game, setGame] = useState<Game | null>(null);
  const [reviewsUpdated, setReviewsUpdated] = useState(0);

  useEffect(() => {
    apiClient.get(`/games/${slug}`).then(res => setGame(res.data.data));
  }, [slug]);

  if (!game) {
    return (
      <div className='loader-wrapper'>
        <div className='loader-spinner'></div>
        <p>ボードゲームの情報を読み込んでいます...</p>
      </div>
    );
  }

  // Fallback image URL
  const imgUrl = game.image_url 
    ? (game.image_url.startsWith('//') ? 'https:' + game.image_url : game.image_url)
    : 'https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?auto=format&fit=crop&q=80&w=600';

  const mechanics = game.structured_data?.mechanics || [];

  return (
    <div className='comparison-container detail-page'>
      <Helmet>
        <title>{`${game.title_ja || game.title} | ボドゲのミカタ`}</title>
        <meta name='description' content={`${game.title_ja || game.title}のプレイ人数、時間、対象年齢、メカニクスなどの詳細データとプレイヤーのレビュー。`} />
      </Helmet>

      <div className='back-nav'>
        <Link to="/" className='back-button'>
          <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          検索一覧に戻る
        </Link>
      </div>

      <div className='detail-grid'>
        {/* Left Card: Image and Base Stats */}
        <div className='detail-card main-info-card'>
          <div className='detail-image-wrapper'>
            <img className='detail-image' src={imgUrl} alt={game.title} />
          </div>
          <div className='detail-main-header'>
            <h1 className='detail-title'>{game.title_ja || game.title}</h1>
            {game.title_ja && <h2 className='detail-subtitle-en'>{game.title}</h2>}
            
            <div className='game-meta' style={{ marginTop: '1.25rem' }}>
              <span className='meta-badge players'>👤 {game.min_players}-{game.max_players}人</span>
              <span className='meta-badge time'>⏱️ {game.play_time}分</span>
              <span className='meta-badge year'>📅 {game.published_year}年</span>
              <span className='meta-badge age'>🔞 {game.min_age}歳以上</span>
            </div>
          </div>
        </div>

        {/* Right Card: Visualization and Description */}
        <div className='detail-card desc-card'>
          <h3>ゲーム概要</h3>
          <p className='game-description'>{game.description || '説明はありません。'}</p>
          
          {mechanics.length > 0 && (
            <div className='mechanics-section'>
              <h4>メカニクス</h4>
              <div className='mechanics-tags'>
                {mechanics.map((m: string, idx: number) => (
                  <span key={idx} className='mechanic-tag'>{m}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Review Section */}
      <div className='review-section-wrapper'>
        <div className='detail-card review-write-card'>
          <ReviewForm slug={slug!} onSubmitted={() => setReviewsUpdated(prev => prev + 1)} />
        </div>
        <div className='detail-card review-list-card'>
          <ReviewList slug={slug!} key={reviewsUpdated} />
        </div>
      </div>
    </div>
  );
};
