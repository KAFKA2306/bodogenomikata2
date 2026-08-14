import type { Game } from '../types/game';

const gigamicRulebookUrl = 'https://en.gigamic.com/index.php?controller=attachment&id_attachment=668';
const gigamicProductUrl = 'https://en.gigamic.com/family-games/1417-ipso.html';
const bgaRulesUrl = 'https://en.boardgamearena.com/gamepanel?game=ipso';

export const curatedGames: Game[] = [
  {
    id: -1,
    slug: 'ipso',
    title: 'Ipso',
    title_ja: 'イプソ',
    description: '数字カードを4段のピラミッドに配置し、各段を左から右へ昇順にそろえて得点するカードゲーム。通常手番では中央の表向き2枚から1枚を選び、自分の裏向きカード1枚と交換する。',
    published_year: 2026,
    min_players: 2,
    max_players: 6,
    play_time: 15,
    min_age: 7,
    editions: ['Gigamic公式ルール 10-2025'],
    structured_data: {
      mechanics: ['カードドラフト', 'セットコレクション', '昇順配置', 'オープンドラフト'],
      source_documents: [
        {
          id: 'ipso-gigamic-rulebook',
          title: 'IPSO Rulebook',
          url: gigamicRulebookUrl,
          version: 'Gigamic公式ルール 10-2025',
          page_or_section: '全2ページ',
          language: 'en',
          source_type: 'OfficialRule',
          review_status: 'reviewed',
        },
        {
          id: 'ipso-gigamic-product',
          title: 'Ipso | Card Game | Gigamic',
          url: gigamicProductUrl,
          version: null,
          page_or_section: 'Description / Details',
          language: 'en',
          source_type: 'OfficialRule',
          review_status: 'reviewed',
        },
        {
          id: 'ipso-bga-rules',
          title: 'IPSO | Board Game Arena',
          url: bgaRulesUrl,
          version: null,
          page_or_section: 'Rules summary',
          language: 'en',
          source_type: 'ExtractedFact',
          review_status: 'reviewed',
        },
      ],
      rule_answers: [
        {
          id: 'ipso-goal',
          question_keywords: ['目的', '勝利条件', 'どう勝つ', '何を目指す'],
          answer: '4段それぞれで、数字カードを左から右へ昇順に並べて得点を作ります。ゲーム終了時に合計得点が最も高いプレイヤーが勝者です。',
          source_ids: ['ipso-gigamic-rulebook'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'ipso-contents-setup',
          question_keywords: ['準備', 'セットアップ', '最初', 'カード枚数', '内容物', 'ピラミッド'],
          answer: '数字カードは1〜90の90枚で、5色それぞれ18枚。星カードは6枚です。数字カードを混ぜ、各プレイヤーに14枚を裏向きで配り、下から5枚・4枚・3枚・2枚の4段ピラミッドを作ります。頂点に星カード1枚を置き、残りを山札にします。',
          source_ids: ['ipso-gigamic-rulebook'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'ipso-turn',
          question_keywords: ['手番', 'ターン', '何する', '中央', '場から', 'カードを選ぶ', '交換'],
          answer: '山札の上から2枚を中央に表向きで置いて開始します。手番では中央の2枚から1枚を選び、自分のピラミッドにある裏向きカード1枚と交換します。交換で取り出したカードを表向きにして中央へ置き、次のプレイヤーへ進みます。最年少のプレイヤーから始め、時計回りです。',
          source_ids: ['ipso-gigamic-rulebook'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'ipso-facedown-only',
          question_keywords: ['表向き', '裏向き', '置き直し', '交換できる', '一度置いた', '変更できる'],
          answer: '通常手番で交換できるのは、自分のピラミッドにある裏向きカードだけです。一度中央から取ってピラミッドへ加えた表向きカードは、通常手番では交換できません。',
          source_ids: ['ipso-gigamic-rulebook'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'ipso-final-round',
          question_keywords: ['星カード', '最終ラウンド', '最後の手番', '最後に引く', '追加手番'],
          answer: '全員のピラミッドがすべて表向きになったら、中央の2枚を山札の一番下へ戻します。各プレイヤーは、星カードを残してゲーム終了時に3点を得るか、星カードを捨てて追加の1手番を行うか選びます。追加手番では山札の一番上を1枚引き、ピラミッドの表向きカード1枚と交換できます。使いたくなければ引いたカードを捨てられますが、その場合も星カードは失います。',
          source_ids: ['ipso-gigamic-rulebook'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'ipso-end-condition',
          question_keywords: ['終了条件', 'いつ終わる', 'ゲーム終了', '終わり', '終了', '何枚開く'],
          answer: '通常進行は、全プレイヤーが自分の14枚のピラミッドカードをすべて表向きにするまで続きます。その後、各プレイヤーが星カードを残すか、星カードを捨てて追加の1手番を行うかを処理します。全プレイヤーがこの最終手番を終えた時点でゲーム終了です。',
          source_ids: ['ipso-gigamic-rulebook', 'ipso-bga-rules'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'ipso-scoring',
          question_keywords: ['得点', '点数', 'スコア', '昇順', '同じ色', '星の点', '何点'],
          answer: '得点できるのは左から右へ昇順になった段だけで、昇順でない段は0点です。有効な段が複数色ならカード1枚につき1点、すべて同色なら1枚につき2点です。有効な段に描かれた星は星1個につき1点。頂点の星カードを残していればさらに3点です。',
          source_ids: ['ipso-gigamic-rulebook'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'ipso-tie',
          question_keywords: ['同点', '引き分け', 'タイブレーク', '同じ点'],
          answer: '合計得点が同点なら、自分の数字カード上にある星の数が多いプレイヤーが勝ちます。それでも同点なら、もう一度プレイします。',
          source_ids: ['ipso-gigamic-rulebook'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'ipso-variants',
          question_keywords: ['ヴァリアント', 'バリアント', '奇数', '偶数', 'トーナメント'],
          answer: '公式ヴァリアントは2つあります。「Odd and even rows」では通常得点後、すべて奇数またはすべて偶数の段にカード1枚につき追加1点。「Tournament mode」では4ゲーム行い、ゲームごとに進行方向を変え、4ゲームの合計得点で勝者を決めます。',
          source_ids: ['ipso-gigamic-rulebook'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
      ],
    },
  },
];

export function findCuratedGameBySlug(slug: string) {
  return curatedGames.find(game => game.slug === slug);
}

export function mergeCuratedGames(games: Game[], query: string, limit: number, offset: number) {
  if (offset !== 0) return games;

  const normalizedQuery = query.normalize('NFKC').toLocaleLowerCase('ja').trim();
  const matches = curatedGames.filter(game => {
    if (!normalizedQuery) return true;
    return game.title.toLocaleLowerCase('ja').includes(normalizedQuery)
      || game.title_ja?.toLocaleLowerCase('ja').includes(normalizedQuery);
  });
  const curatedSlugs = new Set(matches.map(game => game.slug));
  return [...matches, ...games.filter(game => !curatedSlugs.has(game.slug))].slice(0, limit);
}
