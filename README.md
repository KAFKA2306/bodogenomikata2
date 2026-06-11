# 🎲 ボドゲのミカタ (Bodoge no Mikata) v2 🧩

<div align="center">
  <img src="assets/02_ボドゲのミカタ.jpg" alt="ボドゲのミカタ ヘッダー" width="100%" style="border-radius: 12px; border: 1px solid #4ef0c7;">

  ### **「ルールを『読む』苦労から、ボドゲを『遊ぶ』楽しさへ。」**
  **AIがあなたの代わりに膨大なマニュアルを読み込み、瞬時に日本語で図解・要約する究極のコンパニオン。**

  [![License: MIT](https://img.shields.io/badge/License-MIT-4ef0c7?style=for-the-badge&logo=github)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
</div>

---

## 📖 私たちが解決する「4つのストーリー」

ボドゲファンの誰もが直面する悩みを、最新のAIテクノロジーで解決します。

### 1️⃣ インスト時間をゼロに、プレイ時間を最大に
> 厚い説明書を1時間かけて読み、友達に説明するのはもう終わりです。AIが「準備」「進行」「勝利条件」を3分で要約。集まった瞬間、すぐにダイスを振ることができます。

### 2️⃣ 英語ルール・輸入ゲームの壁を破壊
> 海外の新作、BGGで高評価なあのゲーム。英語のPDFマニュアルを渡すだけで、日本語の解説とインフォグラフィック（図解画像）を自動生成。世界の知恵に、あなたの母国語でアクセスできます。

### 3️⃣ プレイ中の「あれ？」をスマホで解決
> 「このアクション、どう処理するんだっけ？」 プレイ中にスマホでサクッと再確認。戦略的な思考を止めることなく、スムーズなゲーム進行をサポートします。

### 4️⃣ 「耳」で聴くルール・インスト
> 準備をしながら、AIの落ち着いた音声でルールの要点をチェック。読み上げ機能が、まるで熟練のインスト担当者が隣にいるような安心感を届けます。

---

## 🔥 主要機能 (Key Features)

- **AI High-Res Reconstruction**: Gemini 2.5 Flashによる、コンテキストを理解した高品質な日本語解説生成。
- **NotebookLM Content Pipeline**: ルールPDFから「セットアップ」「図解」を自動生成する先進のパイプライン。
- **Local-First Speed**: クラウドを介さないSQLiteによる爆速レスポンス。プライバシーと安定性を両立。
- **BGG Integration**: 世界最大のボードゲームDB（BoardGameGeek）からスペック・評価情報をリアルタイム取得。

---

## 🛠️ アーキテクチャ (Architecture)

**「贅肉ゼロ (Zero-Fat)」** の自律型エンジン。

- **Backend**: FastAPI + Python 3.11
- **AI Brain**: Gemini 2.5 Flash / Google NotebookLM
- **Storage**: Local SQLite (`backend/games.db`)
- **Orchestration**: Taskfile / uv

```mermaid
graph TD
    User([ボドゲファン]) <--> API[FastAPI - 爆速サーバー]
    API <--> DB[(Local SQLite - 秘密の書庫)]
    API <--> AI[Gemini / NotebookLM - AI脳]
    API <--> BGG[BGG API - 世界の知恵袋]
```

---

## 📦 クイックスタート (Quick Start)

```bash
# 1. 魔法のセットアップ
task setup

# 2. サーバーを召喚！ (ポート 8000)
task dev

# 3. 好きなゲームを同期・生成 (例: Catan)
curl -X POST "http://localhost:8000/api/games/sync?game_name=Catan"
```
必ず毎回まずweb検索する
---

**Built with ❤️ for all Board Gamers by RuleScribe Games Team**
**「ルールブックの厚さは、もう楽しみの邪魔をさせない。」**
