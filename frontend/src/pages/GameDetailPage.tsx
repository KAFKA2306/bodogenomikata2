import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { ReviewForm } from "../components/ReviewForm";
import { ReviewList } from "../components/ReviewList";
import { fetchGameBySlug } from '../api/gameService';
import { resolveAnswer } from '../ruleAnswerResolver';
import type { Game } from '../types/game';

const siteOrigin = (import.meta.env.VITE_SITE_ORIGIN || 'https://bodogenomikata2.pages.dev').replace(/\/$/, '');

function readPrerenderedGame(slug: string): Game | null {
  const snapshot = document.getElementById('prerendered-game')?.textContent;
  if (!snapshot) return null;

  try {
    const game: Game | null = JSON.parse(snapshot);
    return game?.slug === slug ? game : null;
  } catch (error) {
    if (!(error instanceof SyntaxError)) throw error;
    console.error('Prerendered game data could not be read:', error);
    return null;
  }
}

export const GameDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  return slug ? <GameDetail key={slug} slug={slug} /> : null;
};

function GameDetail({ slug }: { slug: string }) {
  const [game, setGame] = useState(() => readPrerenderedGame(slug));
  const [loadFailed, setLoadFailed] = useState(false);
  const [reviewsUpdated, setReviewsUpdated] = useState(0);

  useEffect(() => {
    let active = true;
    fetchGameBySlug(slug).then(({ data }) => {
      if (data?.slug !== slug) throw new Error(`Unexpected game response for ${slug}`);
      if (active) setGame(data);
    }).catch(error => {
      if (!active) return;
      console.error('Game detail could not be loaded:', error);
      setLoadFailed(true);
    });
    return () => { active = false; };
  }, [slug]);

  if (!game && loadFailed) {
    return (
      <div className='comparison-container detail-page'>
        <p className='workflow-error' role='alert'>ゲーム情報を取得できませんでした。</p>
        <Link to='/research' className='back-button'>検索一覧に戻る</Link>
      </div>
    );
  }

  if (!game) {
    return (
      <div className='loader-wrapper' role='status' aria-live='polite' aria-busy='true'>
        <div className='loader-spinner' aria-hidden='true'></div>
        <p>ボードゲームの情報を読み込んでいます...</p>
      </div>
    );
  }

  const displayTitle = game.title_ja || game.title;
  const hasGameImage = Boolean(game.image_url);
  const imgUrl = game.image_url
    ? (game.image_url.startsWith('//') ? 'https:' + game.image_url : game.image_url)
    : 'https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?auto=format&fit=crop&q=80&w=600';

  const mechanics = game.structured_data?.mechanics || [];
  const ruleQuestion = game.structured_data?.rule_answers?.find(answer => answer.review_status === 'source_checked');
  const ruleSource = game.structured_data?.source_documents?.find(source => ruleQuestion?.source_ids.includes(source.id));
  const ruleKeyword = ruleQuestion?.question_keywords[0];
  const quickRuleSearch = ruleKeyword && ruleSource?.version && ruleSource.language
    && resolveAnswer(game, ruleKeyword, ruleSource.version, ruleSource.language).answer?.id === ruleQuestion?.id
    ? new URLSearchParams({ game: game.slug, version: ruleSource.version, lang: ruleSource.language, q: ruleKeyword })
    : null;
  const canonicalUrl = `${siteOrigin}/game/${encodeURIComponent(game.slug)}`;
  const breadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'ボドゲのミカタ', item: `${siteOrigin}/` },
      { '@type': 'ListItem', position: 2, name: '全ゲーム', item: `${siteOrigin}/games/` },
      { '@type': 'ListItem', position: 3, name: displayTitle, item: canonicalUrl },
    ],
  };

  return (
    <div className='comparison-container detail-page'>
      <Helmet>
        <title>{`${displayTitle} | ボドゲのミカタ`}</title>
        <meta name='description' content={`${displayTitle}のプレイ人数、時間、メカニクスなどの詳細データとプレイヤーのレビュー。`} />
        <link rel='canonical' href={canonicalUrl} />
        <script type='application/ld+json'>{JSON.stringify(breadcrumb)}</script>
      </Helmet>

      <div className='back-nav'>
        <Link to="/research" className='back-button'>
          <svg aria-hidden='true' focusable='false' width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          検索一覧に戻る
        </Link>
      </div>

      {loadFailed && <p role='status'>公開時点のゲーム情報を表示しています。最新情報を取得できませんでした。</p>}

      {quickRuleSearch && (
        <Link
          className="workflow-action detail-rule-link"
          to={{ pathname: '/play', search: quickRuleSearch.toString() }}
        >
          {ruleKeyword}を確認
        </Link>
      )}

      <div className='detail-grid'>
        <aside className='detail-card detail-sidebar' aria-label='ゲーム基本情報'>
          <div className='detail-image-wrapper'>
            <img className='detail-image' src={imgUrl} alt={hasGameImage ? displayTitle : ''} />
          </div>
          <dl className='game-meta detail-sidebar-meta'>
            <div className='meta-badge players'>
              <dt><span aria-hidden='true'>👤</span> 人数</dt>
              <dd>{game.min_players}-{game.max_players}人</dd>
            </div>
            <div className='meta-badge time'>
              <dt><span aria-hidden='true'>⏱️</span> 時間</dt>
              <dd>{game.play_time != null ? `${game.play_time}分` : '不明'}</dd>
            </div>
            <div className='meta-badge year'>
              <dt><span aria-hidden='true'>📅</span> 発売年</dt>
              <dd>{game.published_year}年</dd>
            </div>
            {game.min_age != null && (
              <div className='meta-badge age'>
                <dt><span aria-hidden='true'>🔞</span> 対象年齢</dt>
                <dd>{game.min_age}歳以上</dd>
              </div>
            )}
          </dl>
        </aside>

        <div className='detail-main'>
          <section className='detail-card desc-card' aria-labelledby='game-detail-title'>
            <div className='detail-main-header'>
              <h1 id='game-detail-title' className='detail-title'>{displayTitle}</h1>
              {game.title_ja && <p className='detail-subtitle-en'>{game.title}</p>}
            </div>

            <div className='detail-copy'>
              <h2>ゲーム概要</h2>
              <p className='game-description'>{game.description || '説明はありません。'}</p>
            </div>

            {mechanics.length > 0 && (
              <div className='mechanics-section'>
                <h2>メカニクス</h2>
                <div className='mechanics-tags'>
                  {mechanics.map((m: string, idx: number) => (
                    <span key={idx} className='mechanic-tag'>{m}</span>
                  ))}
                </div>
              </div>
            )}
          </section>

          <div className='review-section-wrapper'>
            <div className='detail-card review-write-card'>
              <ReviewForm slug={slug} onSubmitted={() => setReviewsUpdated(prev => prev + 1)} />
            </div>
            <div className='detail-card review-list-card'>
              <ReviewList slug={slug} key={reviewsUpdated} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
