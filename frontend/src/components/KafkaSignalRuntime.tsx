import { useEffect } from 'react';

const RELEASE = 'kafka-signal-v1.0.0';

function enhance(panel: Element) {
  const available = panel.classList.contains('answer-available');
  const title = panel.querySelector('#answer-title')?.textContent?.trim() || '状態不明';
  const reason = panel.querySelector('.answer-reason')?.textContent?.trim();
  const sources = panel.querySelectorAll('.source-list article').length;
  const signature = JSON.stringify([available, title, reason, sources]);
  const dataset = (panel as HTMLElement).dataset;
  if (dataset.kafkaSignalEnhanced === signature) return;
  dataset.kafkaSignalEnhanced = signature;
  panel.querySelector(':scope > .answer-sequence')?.remove();
  panel.querySelector(':scope > .authority-boundary')?.remove();
  const sequence = document.createElement('ol');
  sequence.className = 'answer-sequence';
  sequence.setAttribute('aria-label', '回答の検証順序');
  const items = [
    ['1 判定', title],
    ['2 例外', reason || '指定版・言語・レビュー条件に一致する範囲だけを適用'],
    ['3 出典', sources ? `${sources}件の確認済み出典` : '適用可能な出典なし'],
    ['4 証拠状態', available ? '確認済み。推測を含めない' : '未確立。回答を拒否'],
    ['5 詳細', available ? '下の出典、版、箇所、言語を確認' : '不足条件と次の確認事項を表示'],
  ];
  items.forEach(([label, value]) => {
    const item = document.createElement('li');
    const heading = document.createElement('strong');
    heading.textContent = label;
    const detail = document.createElement('span');
    detail.textContent = value;
    item.append(heading, detail);
    sequence.append(item);
  });
  panel.append(sequence);
  const authority = document.createElement('p');
  authority.className = 'authority-boundary';
  authority.textContent = 'この回答の話者はキャラクターではありません。公式ルール、抽出事実、翻訳、AI要約、人間レビューを出典種別として分離します。';
  panel.append(authority);
}

export function KafkaSignalRuntime() {
  useEffect(() => {
    document.documentElement.dataset.kafkaSignal = RELEASE;
    let meta = document.querySelector('meta[name="kafka-signal-release"]') as HTMLMetaElement | null;
    if (!meta) {
      meta = document.createElement('meta');
      meta.name = 'kafka-signal-release';
      document.head.append(meta);
    }
    meta.content = RELEASE;
    const run = () => document.querySelectorAll('.answer-panel').forEach(enhance);
    run();
    const observer = new MutationObserver(run);
    observer.observe(document.body, { childList: true, characterData: true, subtree: true });
    return () => observer.disconnect();
  }, []);
  return null;
}
