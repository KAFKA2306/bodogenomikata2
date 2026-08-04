import React, { useEffect, useMemo, useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useSearchParams } from 'react-router-dom';
import { ProductShell } from '../components/ProductShell';
import { fetchGames } from '../api/gameService';
import type { Game, RuleAnswer, RuleSource } from '../types/game';

type PlayModePageProps = { intent: 'play' | 'install' };

type AnswerResult = {
  answer: RuleAnswer | null;
  sources: RuleSource[];
  reason: string | null;
};

const sourceLabels: Record<RuleSource['source_type'], string> = {
  OfficialRule: '公式ルール',
  ExtractedFact: '抽出事実',
  AIGeneratedSummary: 'AI要約',
  Translation: '翻訳',
  HumanReview: '人間レビュー',
  DatabaseObservation: 'DB観測',
};

function normalized(value: string) {
  return value.normalize('NFKC').toLocaleLowerCase('ja').trim();
}

function resolveAnswer(game: Game | undefined, question: string, version: string): AnswerResult {
  if (!game) return { answer: null, sources: [], reason: 'ゲームを選択してください。' };
  if (!version.trim()) return { answer: null, sources: [], reason: '対象の版を指定してください。' };
  if (!question.trim()) return { answer: null, sources: [], reason: '確認したい質問を入力してください。' };

  const documents = game.structured_data?.source_documents || [];
  const answers = game.structured_data?.rule_answers || [];
  const query = normalized(question);
  const answer = answers.find(candidate =>
    candidate.review_status === 'reviewed'
    && candidate.spoiler_level !== 'major'
    && candidate.question_keywords.some(keyword => query.includes(normalized(keyword))),
  ) || null;
  if (!answer) return { answer: null, sources: [], reason: '確認済みの回答が登録されていません。推測では回答しません。' };

  const sources = answer.source_ids
    .map(sourceId => documents.find(document => document.id === sourceId))
    .filter((source): source is RuleSource => Boolean(source))
    .filter(source => source.review_status === 'reviewed');
  if (!sources.length) return { answer: null, sources: [], reason: '回答に紐づく確認済み出典がありません。推測では回答しません。' };

  const versionMatches = sources.some(source => !source.version || normalized(source.version) === normalized(version));
  if (!versionMatches) return { answer: null, sources, reason: `指定版「${version}」と一致する出典を確認できません。` };
  return { answer, sources, reason: null };
}

export const PlayModePage: React.FC<PlayModePageProps> = ({ intent }) => {
  const [params, setParams] = useSearchParams();
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submittedQuestion, setSubmittedQuestion] = useState(params.get('q') || '');
  const gameSlug = params.get('game') || '';
  const version = params.get('version') || '';
  const language = params.get('lang') || 'ja';
  const question = params.get('q') || '';
  const game = games.find(item => item.slug === gameSlug);
  const result = useMemo(() => resolveAnswer(game, submittedQuestion, version), [game, submittedQuestion, version]);

  useEffect(() => {
    let active = true;
    fetchGames('', 200, 0)
      .then(response => { if (active) setGames(response.data); })
      .catch(() => { if (active) setError('ゲーム一覧を読み込めませんでした。'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const updateParam = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value); else next.delete(key);
    setParams(next, { replace: true });
  };

  const editions = game?.editions?.length ? game.editions : [];
  const title = intent === 'play' ? 'プレイ中に確認する' : '開始前に説明する';
  const helper = intent === 'play'
    ? '版と質問を固定し、確認済み出典がある回答だけを表示します。'
    : 'セットアップ、手番、終了条件など、確認済みの短い説明だけを使います。';

  return (
    <ProductShell mainId="play-workspace">
      <Helmet><html lang="ja" /><title>{title} | ボドゲのミカタ</title></Helmet>
      <section className="play-layout" id="play-workspace" tabIndex={-1}>
        <header className="play-heading">
          <p className="workflow-eyebrow">{intent === 'play' ? 'AT THE TABLE' : 'BEFORE PLAY'}</p>
          <h1>{title}</h1>
          <p>{helper}</p>
        </header>

        <section className="play-context" aria-labelledby="context-title">
          <div className="section-heading"><div><p className="workflow-eyebrow">STICKY CONTEXT</p><h2 id="context-title">対象を固定</h2></div><span>URLで共有・再読込可能</span></div>
          <div className="play-context-grid">
            <label><span>ゲーム</span><select value={gameSlug} onChange={event => updateParam('game', event.target.value)} disabled={loading}><option value="">選択してください</option>{games.map(item => <option value={item.slug} key={item.slug}>{item.title_ja || item.title}</option>)}</select></label>
            <label><span>版</span>{editions.length ? <select value={version} onChange={event => updateParam('version', event.target.value)}><option value="">選択してください</option>{editions.map(edition => <option value={edition} key={edition}>{edition}</option>)}</select> : <input value={version} onChange={event => updateParam('version', event.target.value)} placeholder="例：日本語第2版" />}</label>
            <label><span>言語</span><select value={language} onChange={event => updateParam('lang', event.target.value)}><option value="ja">日本語</option><option value="en">English</option></select></label>
          </div>
          {error && <p className="workflow-error" role="alert">{error}</p>}
        </section>

        <section className="question-panel" aria-labelledby="question-title">
          <div className="section-heading"><div><p className="workflow-eyebrow">QUESTION</p><h2 id="question-title">短く質問する</h2></div></div>
          <form onSubmit={event => { event.preventDefault(); setSubmittedQuestion(question); }}>
            <label className="question-field"><span>確認したいこと</span><textarea value={question} onChange={event => updateParam('q', event.target.value)} placeholder={intent === 'play' ? '例：このカードは手番中に何回使えますか？' : '例：最初のセットアップを教えてください'} /></label>
            <button type="submit" className="workflow-action workflow-button">根拠付き回答を確認</button>
          </form>
        </section>

        <section className={`answer-panel ${result.answer ? 'answer-available' : 'answer-unavailable'}`} aria-labelledby="answer-title" aria-live="polite">
          <div className="answer-status"><span aria-hidden="true">{result.answer ? '✓' : '!'}</span><div><p className="workflow-eyebrow">ANSWER STATUS</p><h2 id="answer-title">{result.answer ? '確認済み回答' : '回答できません'}</h2></div></div>
          {result.answer ? (
            <>
              <p className="answer-text">{result.answer.answer}</p>
              <div className="answer-type-row"><span className={`source-type source-type-${result.answer.answer_type}`}>{sourceLabels[result.answer.answer_type]}</span><span className="reviewed-badge">人間レビュー済み</span></div>
              <div className="source-list" aria-label="回答の出典">
                {result.sources.map(source => <article key={source.id}><div><span className={`source-type source-type-${source.source_type}`}>{sourceLabels[source.source_type]}</span><strong>{source.title}</strong></div><dl><div><dt>版</dt><dd>{source.version || '版共通'}</dd></div><div><dt>箇所</dt><dd>{source.page_or_section || '未登録'}</dd></div><div><dt>言語</dt><dd>{source.language || '未登録'}</dd></div></dl>{source.url ? <a href={source.url} target="_blank" rel="noreferrer">出典を開く ↗</a> : <span className="source-missing">URL未登録</span>}</article>)}
              </div>
            </>
          ) : (
            <><p className="answer-reason">{result.reason}</p>{result.sources.length > 0 && <p className="answer-note">別版の出典は存在しますが、指定版へ適用できるとは断定しません。</p>}<div className="answer-next"><strong>次に確認すること</strong><ul><li>ゲームと版が一致しているか</li><li>公式URLとページ・節が登録されているか</li><li>人間レビューが完了しているか</li></ul></div></>
          )}
        </section>

        <aside className="spoiler-boundary" aria-labelledby="spoiler-title"><div><p className="workflow-eyebrow">SPOILER SAFE</p><h2 id="spoiler-title">ネタバレは既定で非表示</h2></div><p>重大なネタバレを含む回答は、このモードの検索結果・読み上げ・回答領域へ表示しません。</p></aside>
      </section>
    </ProductShell>
  );
};
