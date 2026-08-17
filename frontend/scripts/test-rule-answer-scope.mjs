import assert from 'node:assert/strict';
import { resolveAnswer } from '../src/ruleAnswerResolver.ts';

const game = {
  id: 1,
  slug: 'scope-fixture',
  title: 'Scope fixture',
  description: '',
  published_year: 2026,
  min_players: 2,
  max_players: 4,
  play_time: 60,
  editions: ['日本語第2版', 'English Second Edition'],
  structured_data: {
    source_documents: [
      { id: 'ja-v2', title: '日本語第2版', version: '日本語第2版', language: 'ja', source_type: 'OfficialRule', review_status: 'reviewed' },
      { id: 'en-v2', title: 'English Second Edition', version: '日本語第2版', language: 'en', source_type: 'OfficialRule', review_status: 'reviewed' },
      { id: 'ja-v1', title: '日本語初版', version: '日本語初版', language: 'ja', source_type: 'OfficialRule', review_status: 'reviewed' },
      { id: 'missing-scope', title: 'Scope missing', source_type: 'OfficialRule', review_status: 'reviewed' },
      { id: 'pending', title: 'Pending', version: '日本語第2版', language: 'ja', source_type: 'OfficialRule', review_status: 'pending' },
    ],
    rule_answers: [
      {
        id: 'answer',
        question_keywords: ['手番'],
        answer: '確認済み回答',
        source_ids: ['ja-v2', 'en-v2', 'ja-v1', 'missing-scope', 'pending'],
        answer_type: 'OfficialRule',
        review_status: 'reviewed',
        spoiler_level: 'none',
      },
    ],
  },
};

const japanese = resolveAnswer(game, '手番について', '日本語第2版', 'ja');
assert.equal(japanese.answer?.id, 'answer');
assert.deepEqual(japanese.sources.map(source => source.id), ['ja-v2']);

const english = resolveAnswer(game, '手番について', '日本語第2版', 'en');
assert.equal(english.answer?.id, 'answer');
assert.deepEqual(english.sources.map(source => source.id), ['en-v2']);

const wrongVersion = resolveAnswer(game, '手番について', '日本語初版', 'ja');
assert.deepEqual(wrongVersion.sources.map(source => source.id), ['ja-v1']);

const unknownLanguage = resolveAnswer(game, '手番について', '日本語第2版', 'fr');
assert.equal(unknownLanguage.answer, null);
assert.deepEqual(unknownLanguage.sources, []);
assert.match(unknownLanguage.reason || '', /言語/);

const onlyUnscoped = structuredClone(game);
onlyUnscoped.structured_data.rule_answers[0].source_ids = ['missing-scope'];
const unscoped = resolveAnswer(onlyUnscoped, '手番について', '日本語第2版', 'ja');
assert.equal(unscoped.answer, null);
assert.deepEqual(unscoped.sources, []);

console.log('rule answer scope: ok');
