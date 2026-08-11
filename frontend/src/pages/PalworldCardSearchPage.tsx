import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { Helmet } from 'react-helmet-async';
import { apiClient } from '../api/client';
import './palworld-card-search.css';

type Printing = {
  printing_id: string;
  rarity: string;
  is_parallel: boolean;
  official_image_url: string | null;
  source_url: string;
};

type Card = {
  card_base_id: string;
  name_ja: string | null;
  name_en: string;
  card_type: string;
  subtype: string | null;
  color: string;
  cost: number | null;
  power_or_durability: number | null;
  strike: number | null;
  elements: string[];
  aptitudes: string[];
  effect_text_ja: string | null;
  effect_text_en: string | null;
  source_url_en: string;
};

type SearchItem = { card: Card; printings: Printing[] };

type SearchResponse = {
  success: boolean;
  data: SearchItem[];
  pagination: { total: number; count: number };
  manifest: { printing_count: number; logical_card_count: number; source_checked_at: string };
};

export const PalworldCardSearchPage = () => {
  const [query, setQuery] = useState('');
  const [color, setColor] = useState('');
  const [cardType, setCardType] = useState('');
  const [rarity, setRarity] = useState('');
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    setLoading(true);
    const response = await apiClient.get<SearchResponse>('/palworld/cards', {
      params: {
        q: query || undefined,
        color: color || undefined,
        card_type: cardType || undefined,
        rarity: rarity || undefined,
        limit: 200,
      },
    });
    setResult(response.data);
    setLoading(false);
  };

  useEffect(() => {
    void search();
  }, []);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    void search();
  };

  return (
    <section className="palworld-db" aria-labelledby="palworld-db-title">
      <Helmet>
        <title>Palworld OCG カードDB | ボドゲのミカタ</title>
        <meta name="description" content="Palworld OFFICIAL CARD GAME の公式カード情報を出典付きで検索します。" />
      </Helmet>

      <div className="palworld-db-hero">
        <div>
          <p className="palworld-db-kicker">OFFICIAL DATA INDEX</p>
          <h1 id="palworld-db-title">Palworld OCG カードDB</h1>
          <p>カード番号・日英名称・色・種類・レアリティから、公式データに絞って検索できます。</p>
        </div>
        {result && (
          <dl className="palworld-db-counts">
            <div><dt>論理カード</dt><dd>{result.manifest.logical_card_count}</dd></div>
            <div><dt>印刷バリエーション</dt><dd>{result.manifest.printing_count}</dd></div>
          </dl>
        )}
      </div>

      <form className="palworld-db-filters" onSubmit={submit}>
        <label className="palworld-db-query">
          <span>カード番号・名称</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例: EBP01-002SP / Suzaku"
          />
        </label>
        <label>
          <span>色</span>
          <select value={color} onChange={(event) => setColor(event.target.value)}>
            <option value="">すべて</option>
            {['Red', 'Blue', 'Green', 'Purple', 'Colorless'].map((value) => <option key={value}>{value}</option>)}
          </select>
        </label>
        <label>
          <span>種類</span>
          <select value={cardType} onChange={(event) => setCardType(event.target.value)}>
            <option value="">すべて</option>
            {['Pal', 'Structure', 'Event', 'Gear'].map((value) => <option key={value}>{value}</option>)}
          </select>
        </label>
        <label>
          <span>レアリティ</span>
          <select value={rarity} onChange={(event) => setRarity(event.target.value)}>
            <option value="">すべて</option>
            {['RR', 'R', 'U', 'C', 'SSP', 'SP', 'OSR', 'SR'].map((value) => <option key={value}>{value}</option>)}
          </select>
        </label>
        <button type="submit" disabled={loading}>{loading ? '検索中' : '検索'}</button>
      </form>

      <div className="palworld-db-summary" role="status">
        {result ? `${result.pagination.total} 件の論理カード` : '公式カードDBを読み込んでいます'}
      </div>

      <div className="palworld-db-results">
        {result?.data.map(({ card, printings }) => {
          const image = printings.find((printing) => printing.official_image_url)?.official_image_url;
          return (
            <article className="palworld-card" key={card.card_base_id}>
              {image && <img src={image} alt="" loading="lazy" referrerPolicy="no-referrer" />}
              <div className="palworld-card-body">
                <div className="palworld-card-heading">
                  <div>
                    <span className="palworld-card-number">{card.card_base_id}</span>
                    <h2>{card.name_ja || card.name_en}</h2>
                    {card.name_ja && <p className="palworld-card-en">{card.name_en}</p>}
                  </div>
                  <span className="palworld-card-color">{card.color}</span>
                </div>
                <div className="palworld-card-stats">
                  <span>{card.card_type}{card.subtype ? ` / ${card.subtype}` : ''}</span>
                  {card.cost !== null && <span>Cost {card.cost}</span>}
                  {card.power_or_durability !== null && <span>Power/Durability {card.power_or_durability}</span>}
                  {card.strike !== null && <span>Strike {card.strike}</span>}
                </div>
                {(card.elements.length > 0 || card.aptitudes.length > 0) && (
                  <p className="palworld-card-tags">{[...card.elements, ...card.aptitudes].join(' · ')}</p>
                )}
                {(card.effect_text_ja || card.effect_text_en) && (
                  <p className="palworld-card-effect">{card.effect_text_ja || card.effect_text_en}</p>
                )}
                <div className="palworld-card-printings" aria-label="印刷バリエーション">
                  {printings.map((printing) => (
                    <a key={printing.printing_id} href={printing.source_url} target="_blank" rel="noreferrer">
                      {printing.printing_id} · {printing.rarity}
                    </a>
                  ))}
                </div>
                <a className="palworld-card-source" href={card.source_url_en} target="_blank" rel="noreferrer">
                  公式カード詳細を確認
                </a>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
};
