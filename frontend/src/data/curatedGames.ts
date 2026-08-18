import type { Game } from '../types/game';

const yroPublisherUrl = 'https://www.studiosupernova.it/products/yro';
const yroBgaRulesUrl = 'https://en.boardgamearena.com/gamepanel?game=yro';
const gigamicRulebookUrl = 'https://en.gigamic.com/index.php?controller=attachment&id_attachment=668';
const gigamicProductUrl = 'https://en.gigamic.com/family-games/1417-ipso.html';
const bgaRulesUrl = 'https://en.boardgamearena.com/gamepanel?game=ipso';

export const curatedGames: Game[] = [
  {
    id: -2,
    slug: 'yro',
    title: 'YRO',
    title_ja: 'YRO',
    description: '冒険者を雇用して3×3のギルドを作り、配置によるリンクボーナス、戦闘力、魔法・技術・収入・勝利点のエンジンを組み合わせて得点するカード＆コンボゲーム。各ラウンドは同時進行の6フェイズで処理する。',
    published_year: 2024,
    min_players: 1,
    max_players: 5,
    play_time: 6,
    editions: ['BGA 260725-1445'],
    structured_data: {
      mechanics: ['カード配置', 'セットコレクション', 'コンボ', '同時進行', 'エンジンビルド'],
      source_documents: [
        {
          id: 'yro-studio-supernova',
          title: 'YRO | Studio Supernova',
          url: yroPublisherUrl,
          version: null,
          page_or_section: '製品説明',
          language: 'it',
          source_type: 'OfficialRule',
          review_status: 'reviewed',
        },
        {
          id: 'yro-bga-rules',
          title: 'YRO | Board Game Arena',
          url: yroBgaRulesUrl,
          version: 'BGA 260725-1445',
          page_or_section: 'Rules summary / Game description',
          language: 'en',
          source_type: 'ExtractedFact',
          review_status: 'reviewed',
        },
      ],
      rule_answers: [
        {
          id: 'yro-goal',
          question_keywords: ['目的', '勝利条件', 'どう勝つ', '何を目指す'],
          answer: '冒険者を3×3のギルドに配置し、戦闘・カード効果・リンクボーナスなどで勝利点を集めます。ゲーム終了時、残金の変換と終了時得点を含めて最も勝利点が多いプレイヤーが勝者です。',
          source_ids: ['yro-studio-supernova', 'yro-bga-rules'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'yro-setup',
          question_keywords: ['準備', 'セットアップ', '開始時', '初期手札', '最初'],
          answer: '各プレイヤーはプレイヤーボードと戦闘・勝利点・技術・魔法の4マーカーを受け取ります。共有の戦闘・勝利点ボードを中央に置き、各プレイヤーは3金と手札5枚で開始します。クエストカードを表向きに公開します。',
          source_ids: ['yro-bga-rules'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'yro-round-phases',
          question_keywords: ['フェイズ', 'ラウンド', '順番', '進行', '何をする'],
          answer: '1ラウンドは、①捨て札・ドロー、②雇用、③戦闘、④生産、⑤収入、⑥勝利点の6フェイズです。BGAでは各プレイヤーが同時進行で処理します。',
          source_ids: ['yro-bga-rules'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'yro-recruit',
          question_keywords: ['雇用', 'リクルート', '冒険者を雇う', 'カードを出す', '何枚雇える'],
          answer: '雇用フェイズでは手札から0枚・1枚・2枚の冒険者を、カード左上のコストを金で支払って配置できます。配置時の効果と、その配置で完成したリンクボーナスもこのフェイズで解決します。',
          source_ids: ['yro-bga-rules'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'yro-combat',
          question_keywords: ['戦闘', '戦力', '戦闘力', '前列', '何点もらう'],
          answer: 'ギルドの戦闘力は前列の冒険者の戦闘値から決まり、戦闘フェイズで他プレイヤーと比較します。より強いプレイヤーはプレイヤー人数に応じた勝利点を得ます。',
          source_ids: ['yro-bga-rules'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'yro-link-bonus',
          question_keywords: ['リンク', 'リンクボーナス', '派閥', '職業', '3枚', '一列'],
          answer: '同じ派閥または同じ職業を共有する冒険者3枚を一列にそろえると、リンクボーナスを解放できます。YROではカード単体の強さだけでなく、3×3内の配置が重要です。',
          source_ids: ['yro-studio-supernova', 'yro-bga-rules'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'yro-end-condition',
          question_keywords: ['終了条件', 'いつ終わる', 'ゲーム終了', '40点', '9枚', '終わり'],
          answer: '誰かが3×3のギルドを9枚で埋めるか、誰かが40勝利点に到達したラウンドの終了時にゲーム終了です。条件達成の瞬間に即終了するのではありません。',
          source_ids: ['yro-bga-rules'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'yro-after-40',
          question_keywords: ['40点後', '40点に到達', '40点を超えた', '達成後', 'なぜ続く', '即終了'],
          answer: '40勝利点への到達は終了条件を満たしますが、ゲームはそのラウンドの終了時まで続きます。そのため、到達後も残りの戦闘・生産・収入・勝利点フェイズやカード効果を通常どおり処理します。',
          source_ids: ['yro-bga-rules'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
        {
          id: 'yro-money-endgame',
          question_keywords: ['残金', 'お金', '金を得点', '3金', '終了時のお金'],
          answer: 'ゲーム終了時、残っている3金ごとに1勝利点へ変換します。その後、終了時得点を含めた総勝利点で勝者を決めます。',
          source_ids: ['yro-bga-rules'],
          answer_type: 'Translation',
          review_status: 'reviewed',
          spoiler_level: 'none',
        },
      ],
    },
  },
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
    editions: ['Gigamic公式ルール'],
    structured_data: {
      source_documents: [
        {
          id: 'ipso-gigamic-rulebook',
          title: 'IPSO Rulebook',
          url: gigamicRulebookUrl,
          version: 'Gigamic公式ルール',
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