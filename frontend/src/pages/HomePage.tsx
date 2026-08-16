import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import { ProductShell } from '../components/ProductShell';

const modes = [
  {
    to: '/play',
    kicker: 'AT THE TABLE',
    title: 'プレイ中に確認する',
    description: 'ゲーム、版、言語を固定し、短い質問から根拠箇所へ移動します。根拠不足や版不明は回答不能として表示します。',
    action: 'プレイ中モードを開く',
    priority: 'primary',
  },
  {
    to: '/install',
    kicker: 'BEFORE PLAY',
    title: '開始前に説明する',
    description: '人数、時間、概要を確認し、確認済みのセットアップ・手番・終了条件がある場合だけインストに使います。',
    action: '開始前モードを開く',
    priority: 'secondary',
  },
  {
    to: '/research',
    kicker: 'RESEARCH',
    title: '作品・創作を調べる',
    description: '作品検索、メカニクス、公開情報、レビューを扱います。卓上の裁定とは別の探索モードです。',
    action: '作品DBを開く',
    priority: 'secondary',
  },
] as const;

export const HomePage: React.FC = () => (
  <ProductShell>
    <Helmet>
      <html lang="ja" />
      <title>ボドゲのミカタ | 利用モードを選ぶ</title>
      <meta name="description" content="プレイ中、ゲーム開始前、作品・創作調査を分離した出典付きボードゲーム補助。" />
    </Helmet>
    <section className="workflow-hero" aria-labelledby="home-title">
      <p className="workflow-eyebrow">SOURCE-BOUND BOARD GAME COMPANION</p>
      <h1 id="home-title">必要な答えの速さで、<br />入口を分ける。</h1>
      <p>卓上で数秒以内に必要な裁定と、作品を比較する長時間の調査を同じ検索結果へ混ぜません。</p>
    </section>
    <section className="mode-grid" aria-label="利用モード">
      {modes.map(mode => (
        <article className={`mode-card mode-card-${mode.priority}`} key={mode.to}>
          <p className="workflow-eyebrow">{mode.kicker}</p>
          <h2>{mode.title}</h2>
          <p>{mode.description}</p>
          <Link to={mode.to} className="workflow-action">{mode.action}<span aria-hidden="true">→</span></Link>
        </article>
      ))}
    </section>
    <section className="evidence-contract" aria-labelledby="contract-title">
      <div><p className="workflow-eyebrow">ANSWER CONTRACT</p><h2 id="contract-title">回答できる条件</h2></div>
      <ol>
        <li><strong>対象ゲームと版</strong><span>版が不明な回答は裁定として表示しません。</span></li>
        <li><strong>出典URLと箇所</strong><span>ページまたは節を特定できる確認済み資料が必要です。</span></li>
        <li><strong>情報種別</strong><span>公式ルール、抽出事実、AI要約、翻訳、人間レビューを区別します。</span></li>
      </ol>
    </section>
    <p><a href="/games/">収録している全ゲームを見る</a></p>
  </ProductShell>
);
