from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = ROOT / "data" / "murder-mystery" / "popular-100-candidates.yaml"
DEFAULT_OUTPUT = ROOT / "data" / "murder-mystery" / "creative-surface-signals-100.yaml"

SIGNAL_RULES: dict[str, re.Pattern[str]] = {
    "fantasy_or_mythic": re.compile(
        r"魔法|魔王|勇者|騎士|姫|ドラゴン|アリス|悪魔|あくま|天使|ヴァンピ|LYCAN|狼|純血種|"
        r"アポロン|グリム|モビーディック|幻想|四季|魔法少女|聖六花|アルカディア",
        re.IGNORECASE,
    ),
    "explicit_murder_or_mystery": re.compile(
        r"殺人|死体|屍体|探偵|ミステリー|謎|審判|暗躍|虚言|真意|黙示録|暗号",
        re.IGNORECASE,
    ),
    "literary_or_poetic_register": re.compile(
        r"蜃|薔薇|夢|棺|独白|向日葵|恋文|永遠|ソナタ|星|薄明|天辺|極夜|流星|紫陽花|"
        r"ほしのおと|遺志|祝杯|終点|エンドロール|囁く|哭|蛙",
        re.IGNORECASE,
    ),
    "emotion_or_relationship_foreground": re.compile(
        r"恋|愛|純愛|祝杯|独白|気持ち|婚約者|アイドル|家哭|憧れ|最後|永遠|届かない|"
        r"失格|背徳|暴|苦しみ|不在|終わり",
        re.IGNORECASE,
    ),
    "closed_or_specific_location": re.compile(
        r"館|山荘|山脈|学院|学校|図書館|遊園地|病棟|監獄|島|村|404号室|地点|急行|街|"
        r"海の上|晩餐会|仮面舞踏会",
        re.IGNORECASE,
    ),
    "sf_or_modern_system": re.compile(
        r"20xx|近未来|World End|NOBODY|404|ゼロから|巻き戻|飛行艇|ALL GREEN|"
        r"レッドストランド|機械|ガラクタ|Deus ex Magia|終点|エンドロール|サイレンズ",
        re.IGNORECASE,
    ),
    "comedy_or_absurd_register": re.compile(
        r"多すぎる|ドタバタ|合コン|くっころ|お嬢様|わたくしではなくってよ|悪の組織|"
        r"クズ|鯖缶|誰にゃ|遊んでいただけませんか|気の毒なアイドル|勇者がいる|高級",
        re.IGNORECASE,
    ),
    "meta_or_form_signal": re.compile(
        r"マダミス|マーダーミステリー|エンドロール|ゴーストライター|独白|晩餐会|"
        r"探偵たち|時間ドロボウ|World End|終点|この恋文|このマーダーミステリー",
        re.IGNORECASE,
    ),
}

SIGNAL_DEFINITIONS = {
    "fantasy_or_mythic": "神話、魔法、勇者、怪物、童話的固有語など。",
    "explicit_murder_or_mystery": "殺人、死体、探偵、謎、審判など事件・推理を明示する語。",
    "literary_or_poetic_register": "比喩性、詩的語彙、余韻を持つ題名表現。",
    "emotion_or_relationship_foreground": "愛、恋、後悔、関係、喪失などを前景化する語。",
    "closed_or_specific_location": "館、学校、村、島、病棟など具体的な舞台を示す語。",
    "sf_or_modern_system": "近未来、時間操作、システム、機械、終端など。",
    "comedy_or_absurd_register": "誇張、口語、パロディ、不条理を示す題名表現。",
    "meta_or_form_signal": "作品形式、語り、上映、執筆、マダミス自体を示す語。",
    "unclassified_title_surface": "単純な語彙規則では分類しない。",
}

PROHIBITED_INFERENCES = {
    "qualityScore",
    "surpriseFairness",
    "emotionalPayoff",
    "narrativeCoherence",
    "humanAuthored",
    "aiAuthored",
    "aiGeneratedProbability",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def classify_title(title: str) -> list[str]:
    signals = [name for name, pattern in SIGNAL_RULES.items() if pattern.search(title)]
    return signals or ["unclassified_title_surface"]


def analyze_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    works = corpus.get("works")
    if not isinstance(works, list) or len(works) != 100:
        raise ValueError("creative surface analysis requires exactly 100 source works")

    expected_ids = [f"mmc-{index:03d}" for index in range(1, 101)]
    actual_ids = [work.get("id") for work in works]
    if actual_ids != expected_ids:
        raise ValueError("source works must use sequential IDs mmc-001 through mmc-100")

    analyzed_works: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for source_work in works:
        title = source_work.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{source_work.get('id')}: title is required")
        signals = classify_title(title)
        counts.update(signals)
        analyzed_works.append(
            {
                "workId": source_work["id"],
                "title": title,
                "evidenceLevel": "title_only",
                "titleSurfaceSignals": signals,
                "interpretationPolicy": "signal_not_content_claim",
                "notAssessed": sorted(PROHIBITED_INFERENCES),
            }
        )

    return {
        "metadata": {
            "id": "kafka:madamis-creative-surface-signals-100",
            "title": "マダミス100作 タイトル表層シグナル",
            "version": "0.1.0",
            "updated": "2026-08-02",
            "recordCount": 100,
            "purpose": (
                "100作品を同じ基準で一次コーディングする。タイトルから観測できる語彙・形式シグナルだけを記録し、"
                "内容、品質、作者性、AI利用を推定しない。"
            ),
            "sourceCorpus": str(DEFAULT_CORPUS.relative_to(ROOT)),
            "evidenceLevel": "title_only",
            "warning": "titleSurfaceSignalsは作品内容の断定、創作性評価、人気順位、AI利用判定ではない。",
        },
        "signalDefinitions": SIGNAL_DEFINITIONS,
        "summaryCounts": dict(counts),
        "works": analyzed_works,
    }


def validate_analysis(analysis: dict[str, Any]) -> None:
    works = analysis.get("works")
    if not isinstance(works, list) or len(works) != 100:
        raise ValueError("analysis must contain exactly 100 works")
    for work in works:
        if work.get("evidenceLevel") != "title_only":
            raise ValueError(f"{work.get('workId')}: generated analysis must remain title_only")
        if set(work) & PROHIBITED_INFERENCES:
            raise ValueError(f"{work.get('workId')}: prohibited inference field detected")
        if not work.get("titleSurfaceSignals"):
            raise ValueError(f"{work.get('workId')}: at least one surface signal is required")


def write_analysis(analysis: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(analysis, handle, allow_unicode=True, sort_keys=False, width=120)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze title-surface signals for the 100-work murder-mystery corpus")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Validate without writing an output file")
    args = parser.parse_args()

    analysis = analyze_corpus(load_yaml(args.corpus))
    validate_analysis(analysis)
    if not args.check:
        write_analysis(analysis, args.output)
    print("murder-mystery creative surface analysis: OK")
    for signal, count in sorted(analysis["summaryCounts"].items()):
        print(f"{signal}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
