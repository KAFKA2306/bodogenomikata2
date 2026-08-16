import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import ts from 'typescript';

const here = path.dirname(fileURLToPath(import.meta.url));
const dist = path.resolve(here, '../../static');
const origin = (process.env.SITE_ORIGIN || process.env.VITE_SITE_ORIGIN || 'https://bodoge-no-mikata.vercel.app').replace(/\/$/, '');

const esc = (value = '') => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#39;');
const xml = esc;
const jsonLd = (value) => JSON.stringify(value).replaceAll('<', '\\u003c');
const canonical = (pathname) => `${origin}${pathname}`;

const gamesRaw = JSON.parse(await readFile(path.join(dist, 'data.json'), 'utf8'));
if (!Array.isArray(gamesRaw)) throw new Error('static/data.json must be an array');

const curatedSource = await readFile(path.resolve(here, '../src/data/curatedGames.ts'), 'utf8');
const curatedJs = ts.transpileModule(curatedSource, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
}).outputText;
const curatedModule = await import(`data:text/javascript;base64,${Buffer.from(curatedJs).toString('base64')}`);
const curatedGames = curatedModule.curatedGames;
if (!Array.isArray(curatedGames)) throw new Error('curatedGames must be an array');

// Match runtime behavior: curated games are canonical for their slugs and may exist outside data.json.
const gamesBySlug = new Map();
for (const game of gamesRaw) {
  const slug = typeof game?.slug === 'string' ? game.slug.trim() : '';
  if (slug && !gamesBySlug.has(slug)) gamesBySlug.set(slug, game);
}
for (const game of curatedGames) {
  const slug = typeof game?.slug === 'string' ? game.slug.trim() : '';
  if (!slug) throw new Error('curated game without slug');
  gamesBySlug.set(slug, game);
}
const games = [...gamesBySlug.values()];

const template = await readFile(path.join(dist, 'index.html'), 'utf8');
const replaceHead = (html, { title, description, url, structuredData }) => {
  let next = html
    .replace(/<title>[\s\S]*?<\/title>/i, `<title>${esc(title)}</title>`)
    .replace(/<meta\s+name=["']description["'][^>]*>/i, `<meta name="description" content="${esc(description)}" />`);
  const extras = [
    `<link rel="canonical" href="${esc(url)}" />`,
    structuredData ? `<script type="application/ld+json">${jsonLd(structuredData)}</script>` : '',
  ].filter(Boolean).join('\n    ');
  return next.replace('</head>', `    ${extras}\n  </head>`);
};

const gamePath = (slug) => `/game/${encodeURIComponent(slug)}`;
const missingMetadata = games.filter((g) => !(g.title_ja || g.title) || g.min_players == null || g.max_players == null || g.play_time == null).length;

for (const game of games) {
  const slug = game.slug.trim();
  const pathname = gamePath(slug);
  const url = canonical(pathname);
  const title = game.title_ja || game.title || slug;
  const description = game.description || `${title}のプレイ人数、時間、メカニクスなどの詳細データ。`;
  const mechanics = Array.isArray(game.structured_data?.mechanics) ? game.structured_data.mechanics : [];
  const breadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'ボドゲのミカタ', item: canonical('/') },
      { '@type': 'ListItem', position: 2, name: '全ゲーム', item: canonical('/games/') },
      { '@type': 'ListItem', position: 3, name: title, item: url },
    ],
  };

  const details = [
    game.min_players != null && game.max_players != null ? `<div><dt>人数</dt><dd>${esc(game.min_players)}-${esc(game.max_players)}人</dd></div>` : '',
    game.play_time != null ? `<div><dt>時間</dt><dd>${esc(game.play_time)}分</dd></div>` : '',
    game.published_year != null ? `<div><dt>発売年</dt><dd>${esc(game.published_year)}年</dd></div>` : '',
  ].filter(Boolean).join('');
  const mechanicsHtml = mechanics.length ? `<section><h2>メカニクス</h2><ul>${mechanics.map((m) => `<li>${esc(m)}</li>`).join('')}</ul></section>` : '';
  const staticContent = `<main class="comparison-container detail-page" data-prerendered-game="${esc(slug)}"><nav><a href="/games/">全ゲーム一覧</a></nav><article><h1>${esc(title)}</h1><dl>${details}</dl><section><h2>ゲーム概要</h2><p>${esc(description)}</p></section>${mechanicsHtml}</article></main>`;

  const html = replaceHead(template, {
    title: `${title} | ボドゲのミカタ`,
    description: `${title}のプレイ人数、時間、メカニクスなどの詳細データとプレイヤーのレビュー。`,
    url,
    structuredData: breadcrumb,
  }).replace(/<div id="root"><\/div>/i, `<div id="root">${staticContent}</div>`);

  const outDir = path.join(dist, 'game', encodeURIComponent(slug));
  await mkdir(outDir, { recursive: true });
  await writeFile(path.join(outDir, 'index.html'), html);
}

const gameLinks = games
  .sort((a, b) => String(a.title_ja || a.title || a.slug).localeCompare(String(b.title_ja || b.title || b.slug), 'ja'))
  .map((game) => `<li><a href="${gamePath(game.slug.trim())}">${esc(game.title_ja || game.title || game.slug)}</a></li>`)
  .join('\n');
const gamesIndex = `<!doctype html><html lang="ja"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width,initial-scale=1" /><title>全ゲーム一覧 | ボドゲのミカタ</title><meta name="description" content="ボドゲのミカタに収録しているボードゲームの一覧。" /><link rel="canonical" href="${canonical('/games/')}" /></head><body><main><p><a href="/">ボドゲのミカタ</a></p><h1>全ゲーム一覧</h1><p>${games.length}件</p><ul>${gameLinks}</ul></main></body></html>`;
await mkdir(path.join(dist, 'games'), { recursive: true });
await writeFile(path.join(dist, 'games', 'index.html'), gamesIndex);

const website = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'ボドゲのミカタ',
  url: canonical('/'),
};
const home = replaceHead(template, {
  title: 'ボドゲのミカタ | 出典付きボードゲーム補助',
  description: 'プレイ中、ゲーム開始前、作品調査を分離し、確認済み出典がある回答だけを表示するボードゲーム補助。',
  url: canonical('/'),
  structuredData: website,
});
await writeFile(path.join(dist, 'index.html'), home);

// Only URLs with explicit, generated canonical HTML enter the sitemap.
const staticPaths = ['/', '/games/'];
const paths = [...staticPaths, ...games.map((game) => gamePath(game.slug.trim()))];
if (new Set(paths).size !== paths.length) throw new Error('duplicate canonical URLs detected');

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${paths.map((pathname) => `  <url><loc>${xml(canonical(pathname))}</loc></url>`).join('\n')}\n</urlset>\n`;
await writeFile(path.join(dist, 'sitemap.xml'), sitemap);
await writeFile(path.join(dist, 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${canonical('/sitemap.xml')}\n`);

console.log(`[seo] data.json games: ${gamesRaw.length}`);
console.log(`[seo] curated games: ${curatedGames.length}`);
console.log(`[seo] effective unique game URLs: ${games.length}`);
console.log(`[seo] prerendered game pages: ${games.length}`);
console.log(`[seo] missing core metadata: ${missingMetadata}`);
console.log(`[seo] static URLs: ${staticPaths.length}`);
console.log(`[seo] sitemap URLs: ${paths.length}`);
