import type { Game, RuleAnswer, RuleSource } from './types/game.ts';

export type AnswerResult = {
  answer: RuleAnswer | null;
  sources: RuleSource[];
  reason: string | null;
};

function normalized(value: string) {
  return value.normalize('NFKC').toLocaleLowerCase('ja').trim();
}

function sourceMatchesScope(source: RuleSource, version: string, language: string) {
  return Boolean(
    source.version
    && source.language
    && normalized(source.version) === normalized(version)
    && normalized(source.language) === normalized(language),
  );
}

export function resolveAnswer(
  game: Game | undefined,
  question: string,
  version: string,
  language: string,
): AnswerResult {
  if (!game) return { answer: null, sources: [], reason: 'ゲームを選択してください。' };
  if (!version.trim()) return { answer: null, sources: [], reason: '対象の版を指定してください。' };
  if (!language.trim()) return { answer: null, sources: [], reason: '対象の言語を指定してください。' };
  if (!question.trim()) return { answer: null, sources: [], reason: '確認したい質問を入力してください。' };

  const documents = game.structured_data?.source_documents || [];
  const answers = game.structured_data?.rule_answers || [];
  const query = normalized(question);
  const candidates = answers.filter(candidate =>
    candidate.review_status === 'reviewed'
    && candidate.spoiler_level !== 'major'
    && candidate.question_keywords.some(keyword => query.includes(normalized(keyword))),
  );
  if (!candidates.length) {
    return { answer: null, sources: [], reason: '確認済みの回答が登録されていません。推測では回答しません。' };
  }

  for (const answer of candidates) {
    const sources = answer.source_ids
      .map(sourceId => documents.find(document => document.id === sourceId))
      .filter((source): source is RuleSource => Boolean(source))
      .filter(source => source.review_status === 'reviewed')
      .filter(source => sourceMatchesScope(source, version, language));
    if (sources.length) return { answer, sources, reason: null };
  }

  return {
    answer: null,
    sources: [],
    reason: `指定版「${version}」・言語「${language}」に一致する確認済み出典がありません。`,
  };
}
