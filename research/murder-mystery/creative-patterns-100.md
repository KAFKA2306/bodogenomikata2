# マダミス100作の創作性・人間的手触り調査

更新日: 2026-08-02  
対象: `data/murder-mystery/popular-100-candidates.yaml` の100作品  
公開範囲: タイトル、公式・販売ページの公開あらすじ、公開システム説明、非ネタバレ情報

## 結論

この100作から観測される創作性は、単に「珍しい設定を選ぶこと」ではない。公開情報で確認できる主要な制作操作は次の6群に集約できる。

1. **形式を作品世界の中へ取り込む**  
   Web検索、依頼文、マダミス自体、VRサービス終了、実演などを、外付け演出ではなく事件・手掛かり・感情へ組み込む。

2. **人間関係をゲーム構造にする**  
   姫と騎士、相棒、同僚、創作仲間、シェアハウス住人などの依存関係を、密談、選択、投票、個別結末へ変換する。

3. **相反する感情やジャンルを衝突させる**  
   可愛さと死、喜劇と死体、恋愛と殺人、救済と自己中心性、不死と死など、単一の感情へ整理しない。

4. **生活・職業・共同体の具体性を持たせる**  
   任侠、創作活動、階級社会、サーカス、学校、共同生活など、人物が抽象的な「容疑者機能」だけにならない環境を作る。

5. **不快さ、未解決感、損失を残すリスクを取る**  
   幸福や救済を保証しない、正解を知っても罪や依存が残る、誰かの選択が取り返せない、といった余剰を設計する。

6. **本文外の制作を統合する**  
   専用Web、オリジナル音楽、版の改稿、難易度別版、舞台・小説・ADVへの展開などを作品体験へ接続する。

「AIらしくなさ」は作者判定ではない。見るべきなのは、固有の語彙、社会的具体性、矛盾した感情、作者が取った表現上のリスク、置換しにくい形式である。生成AI補助を公開している作品にも強い固有語彙や世界設計はあり、AI利用の有無と人間的手触りは同一軸ではない。

## 調査方法

### 全100作

全100作を、タイトルから観測できる表層シグナルだけで同一規則により一次コーディングした。これは内容評価ではない。

| タイトル表層シグナル | 該当作数 |
|---|---:|
| ファンタジー・神話的語彙 | 26 |
| 殺人・推理の明示 | 25 |
| 文学的・詩的レジスター | 20 |
| 感情・関係性の前景化 | 18 |
| 閉鎖空間・具体的舞台 | 18 |
| SF・近未来・システム語彙 | 14 |
| メタ形式のシグナル | 11 |
| 喜劇・不条理レジスター | 10 |

一作品は複数シグナルへ該当する。`scripts/analyze_murder_mystery_creativity.py`で100作のレコードを再生成できる。

### 公開情報を確認できた38作

次の表は、公開あらすじや公開システム説明から確認できる**制作上の約束・構造**を記録したものであり、実際の完成度を採点したものではない。

| # | 作品 | 公開情報から確認できる制作操作 | 分析軸 | 根拠レベル | 出典 |
|---:|---|---|---|---|---|
| 1 | 蜃より出づるは夢か現か | 戦国期の主従関係と処刑の切迫を推理へ接続 | `historical_reframing / lived_social_specificity` | `public_synopsis` | [公開情報](https://manaitahodoki.booth.pm/items/1884680) |
| 2 | 探偵が多すぎる | 探偵過剰というパロディ前提。改訂でカード・目的・エンドを追加 | `comedy_or_absurd / versioned_revision` | `public_system_description` | [公開情報](https://toga.booth.pm/items/2106739) |
| 3 | 背徳の代紋 | 任侠の言語・継承争い・自由な嘘・密談を一体化 | `social_system_simulation / lived_social_specificity` | `public_system_description` | [公開情報](https://hikimiya.booth.pm/items/2695449) |
| 4 | バロン・サムディと賑やかな死体の謎 | 死体が蘇って会話するという反転をホラーと喜劇の衝突に使う | `tonal_collision / rule_shift` | `public_synopsis` | [公開情報](https://ccfolia.booth.pm/items/2659031) |
| 5 | 幽刻館の殺人 | 孤島・怪談・密室という本格推理とオカルト曖昧性を併置 | `familiar_genre_specificity / interpretive_range` | `public_synopsis` | [公開情報](https://zareshima.booth.pm/items/2576819) |
| 6 | Nの真意 | 同じ探偵事務所で積み上げた関係史と秘めた感情を事件動機へ接続 | `attachment_through_history / relational_dependency` | `public_synopsis` | [公開情報](https://yuuuri.booth.pm/items/3810870) |
| 7 | 蒸気の街には薔薇が咲く | 蒸気都市、機械人形、階級差、交渉、個別結末を統合 | `setting_specificity / social_system_simulation` | `public_system_description` | [公開情報](https://niseika.booth.pm/items/3618368) |
| 8 | 夢ノ棺ノ時間ドロボウ | 記憶喪失と身份の空白を中心に、多職種チームと再編集で制作 | `identity_reveal_promise / multi_role_team` | `public_system_description` | [公開情報](https://toriemostab.booth.pm/items/2608835) |
| 9 | エイダ | 五種族・五国家の非対称文化と和平会議を事件構造へ組み込む | `social_system_simulation / setting_specificity` | `public_synopsis` | [公開情報](https://itohaki.com/eidaspecial/) |
| 10 | アンノウン | 三時間前へつながるワームホールと未来の死体で因果を反転 | `causal_reversal / relationship_pair_architecture` | `public_synopsis` | [公開情報](https://sakubey.booth.pm/items/2836406) |
| 11 | 裂山荘殺人事件 | マダミス参加者が現実の殺人へ遭遇する自己言及的構図 | `meta_diegetic_address / participatory_reveal` | `public_synopsis` | [公開情報](https://colcolors.booth.pm/items/6343878) |
| 12 | 狂気山脈　陰謀の分水嶺 | 極限環境そのものを圧力にし、登山・宇宙的恐怖・推理を融合 | `environment_as_pressure / cross_genre_combination` | `public_synopsis` | [公開情報](https://dappleox.booth.pm/items/1980320) |
| 13 | 星ふる天辺 | 前作経験と記憶をシリーズ体験へ持ち越す | `serial_memory / transmedia_expansion` | `public_synopsis` | [公開情報](https://dappleox.booth.pm/items/2276640) |
| 14 | LYCAN | 閉鎖村落の役職・血縁・来訪者の不透明な正体を相互作用へ変換 | `relationship_structure / identity_opacity` | `public_synopsis` | [公開情報](https://terazon.booth.pm/items/1815518) |
| 15 | 少年少女Aの独白 | 一人の探偵役へ判断責任を集約し、他者がその判断を導く | `asymmetric_agency / moral_responsibility` | `public_system_description` | [公開情報](https://violetsogabe.booth.pm/items/1895555) |
| 16 | 円蓋の向日葵 | 禁酒法時代のサーカスと、死を見世物として提示する舞台性 | `historical_spectacle / performance_reality_collision` | `public_synopsis` | [公開情報](https://biscuitcocoa.booth.pm/items/2333533) |
| 17 | 最後のソナタ | ピアノコンクールと実演を作品体験へ接続 | `physical_performance_integration / low_replaceability` | `public_synopsis` | [公開情報](https://elkurin.booth.pm/items/6099565) |
| 18 | 屍体に囁く | 架空SNS・ブログ・ニュースを検索して証拠を集めるWeb内世界 | `media_form_innovation / custom_web_investigation` | `public_system_description` | [公開情報](https://booth.pm/ja/items/3189462) |
| 19 | 怪盗エイプリルと七人の探偵たち | 怪盗劇、群像探偵、時間を越える予告状を組み合わせる | `cross_genre_combination / ensemble_archetype` | `public_synopsis` | [公開情報](https://booth.pm/ja/items/4058480) |
| 20 | World End | サービス終了直前のVR世界、ログアウト不能、死を重ねる | `digital_social_identity / service_closure_melancholy` | `public_synopsis` | [公開情報](https://booth.pm/ja/items/7406889) |
| 21 | この恋文は届かない。 | 学校の恋愛伝承と死を結び、結末を参加者の選択へ委ねる | `romance / player_responsibility` | `public_system_description` | [公開情報](https://booth.pm/ja/items/4676495) |
| 22 | 永遠という名の殺人 | 不死の魔女の死という矛盾を物語体験の核にする | `semantic_paradox / fairy_tale_register` | `public_synopsis` | [公開情報](https://booth.pm/ja/items/7196978) |
| 23 | 騎士と四季の姫君と | 四季の国と姫・騎士の対関係、密談、専用楽曲を統合 | `relationship_pair_architecture / original_music` | `public_system_description` | [公開情報](https://booth.pm/ja/items/4916451) |
| 24 | アポロンの審判 | 人狼、マダミス、ストーリープレイングを明示的に混成 | `genre_hybrid / expectation_fit_risk` | `public_system_description` | [公開情報](https://booth.pm/ja/items/6508051) |
| 25 | 魔王討伐前夜の殺人 | RPG最終決戦の直前に勇者が死ぬというクライマックス反転 | `genre_inversion / group_failure` | `public_synopsis` | [公開情報](https://booth.pm/ja/items/4058609) |
| 26 | 夜の蛙は眠らない | 創作を志す若者の日常と夢を事件より前景化 | `creative_labor / lived_social_specificity` | `public_synopsis` | [公開情報](https://booth.pm/ja/items/3528073) |
| 27 | NOBODY | 存在しない「NOBODY」の殺人という言語的不能を出発点にする | `semantic_paradox / literary_adaptation` | `public_synopsis` | [公開情報](https://booth.pm/ja/items/5457771) |
| 28 | このマーダーミステリーを遊んでいただけませんか | 行方不明者の友人からの依頼として、作品自体を手掛かり化 | `meta_diegetic_address / media_form_innovation` | `public_synopsis` | [公開情報](https://booth.pm/ja/items/7753099) |
| 29 | 家哭‐YAKOKU‐ | 救済や幸福を約束しない「不快」を明示し、負の余韻を設計 | `authorial_risk / no_catharsis` | `public_system_description` | [公開情報](https://trsknoha.booth.pm/items/5009463) |
| 30 | エンドロールは流れない | 人造存在が友人の部品を利用した罪と、次の犠牲判断を扱う | `post_human_empathy / moral_residue` | `public_synopsis` | [公開情報](https://booth.pm/ja/items/4478359) |
| 31 | 愛暴 | マフィアのペア依存と継承競争をPvP・交渉へ落とす | `pair_dependency / competitive_social_system` | `public_system_description` | [公開情報](https://harudomannaka1.booth.pm/items/7309212) |
| 32 | 404号室の黙示録 | 交流の薄いシェアハウス住人の事情を対話と選択で掘る | `modern_loneliness / subtext_promise` | `public_system_description` | [公開情報](https://ynmdms.booth.pm/items/7201795) |
| 33 | ほしのおと | 死者と可愛らしい神の組合せで、死と癒しを衝突させる | `cute_death_dissonance / concentrated_intimacy` | `public_synopsis` | [公開情報](https://booth.pm/ja/items/5056376) |
| 34 | 悪の組織は(ま)とまらない！ | 悪役幹部会議を明るい会話劇へ反転し、難易度別版を用意 | `genre_inversion / accessibility_edition` | `public_system_description` | [公開情報](https://booth.pm/ja/items/5936168) |
| 35 | アタシの高級鯖缶たべたの誰にゃ!!? | 猫組織の語彙・事件・役割を一貫させた喜劇。本作は背景等への生成AI補助を公開表示 | `idiosyncratic_register / disclosed_ai_assistance` | `public_system_description` | [公開情報](https://booth.pm/ja/items/8013265) |
| 36 | 馬鹿だね、魔法少女みたいな顔して | 自己中心的な魔法と救済可能性を対立させ、別形式ADVへ展開 | `emotional_contradiction / transmedia_adaptation` | `public_synopsis` | [公開情報](https://booth.pm/ja/items/3928608) |
| 37 | 魔法少女は死んでいる | 魔法少女を国家軍事力として再定義し、相棒関係と進路選択を扱う | `political_reframing / pair_dependency` | `public_synopsis` | [公開情報](https://bluesonia.booth.pm/items/4481888) |
| 38 | 善良村の殺人 | 善人しかいないという共同体ラベルと殺人者の存在を矛盾させる | `moral_paradox / social_system_simulation` | `public_synopsis` | [公開情報](https://booth.pm/ja/items/4720542) |

## 100作から導いた創作分析軸

### 制作技法

- 情報配布と密談の設計
- 人数に対する役割の見せ場
- プレイヤーの選択が結末へ及ぼす範囲
- 改稿履歴と版差
- GMレス化・自動進行・難易度別版
- 音楽、Web、実演、物理アイテムの統合

### 独自性

- `premise_novelty`: 一行前提の新規性
- `setting_specificity`: 他の舞台へ置換しにくい具体性
- `relationship_novelty`: 関係性そのものの設計
- `interaction_novelty`: 参加者の行動形式の新規性
- `formal_novelty`: マダミスの形式自体への操作
- `low_replaceability`: 名前や背景を交換すると成立しなくなる度合い

### 人間的手触り

- `lived_social_specificity`: 生活、職業、共同体の具体性
- `emotional_contradiction`: 愛と加害、救済と利己などの共存
- `relational_dependency`: 一人では完結しない関係
- `moral_ambiguity`: 正解と善悪が一致しない
- `authorial_risk`: 不快、失敗、嫌われる可能性を引き受ける
- `unresolved_residue`: 終了後も割り切れないものが残る
- `idiosyncratic_voice`: 他作品へ置換しにくい固有語彙や語り口

これらはAI利用の有無を示さない。作者性や制作プロセスは、権利者の明示、制作記録、クレジットなど別の来歴情報で扱う。

### 驚かせ方

- 死体や被害者の役割反転
- 時間因果の反転
- 正体や視点の不透明化
- ルールやジャンルの転換
- 言語的・存在論的な矛盾
- プレイヤー自身やプレイ形式の物語内化
- 過去の場面を別の意味へ読み替えさせる構造

公開あらすじから分かるのは「どの方式を約束しているか」までである。伏線の公平性、開示タイミング、再解釈の強さは実プレイまたは許諾された本文監査が必要。

### 感動のさせ方

- 既に共有された関係史への愛着
- ペア・相棒への依存
- 選択責任と取り返しのつかなさ
- 喪失、罪、犠牲、赦し
- 創作や夢への投資
- 可愛さと死、恋愛と事件などの感情衝突
- 救済を与えない負の余韻
- 人間以外の存在への共感

「悲しい設定がある」ことと「感動が成立する」ことは別である。実際に感情が積み上がるか、説明過多でないか、選択が感情へ接続するかはプレイ後評価で確認する。

## 評価してはいけない項目

公開ページだけでは、次を断定しない。

- 伏線の公平性
- 真相の驚き
- 推理の論理整合性
- 手掛かりの過不足
- 実際の会話の人間らしさ
- 感動が十分に積み上がるか
- エンディングの回収力
- AI生成か人間制作か
- 作品の総合的な優劣

## 次の監査単位

各作品は今後、次の順序で精度を上げる。

1. `title_only`
2. `public_synopsis`
3. `public_system_description`
4. `non_spoiler_review`
5. `full_play`
6. `authorized_text`

低い根拠レベルから高い根拠レベルの評価を推定してはならない。点数を付ける場合は、作品版、評価者、日時、具体的な観測、ネタバレ隔離を必須とする。
