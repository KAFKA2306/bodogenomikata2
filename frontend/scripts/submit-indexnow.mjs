import { execFileSync } from 'node:child_process';
import ts from 'typescript';

const origin = (process.env.SITE_ORIGIN || 'https://bodogenomikata2.pages.dev').replace(/\/$/, '');
const key = process.env.INDEXNOW_KEY?.trim();
if (!key) throw new Error('INDEXNOW_KEY is required');
if (!/^[A-Za-z0-9-]{8,128}$/.test(key)) throw new Error('INDEXNOW_KEY must be 8-128 letters, numbers, or dashes');

const beforeRef = process.argv[2] || 'HEAD^';
const afterRef = process.argv[3] || 'HEAD';
const readRef = (ref, file) => execFileSync('git', ['show', `${ref}:${file}`], { encoding: 'utf8' });

const parseCurated = async (source) => {
  const js = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  return (await import(`data:text/javascript;base64,${Buffer.from(js).toString('base64')}`)).curatedGames;
};

const loadInventory = async (ref) => {
  const dataGames = JSON.parse(readRef(ref, 'frontend/public/data.json'));
  const curatedGames = await parseCurated(readRef(ref, 'frontend/src/data/curatedGames.ts'));
  const inventory = new Map();
  for (const game of dataGames) if (game?.slug) inventory.set(game.slug.trim(), game);
  for (const game of curatedGames) if (game?.slug) inventory.set(game.slug.trim(), game);
  return inventory;
};

const before = await loadInventory(beforeRef);
const after = await loadInventory(afterRef);
const slugs = new Set([...before.keys(), ...after.keys()]);
const changed = [...slugs].filter((slug) => JSON.stringify(before.get(slug)) !== JSON.stringify(after.get(slug)));
if (!changed.length) {
  console.log('[indexnow] changed game URLs: 0');
  process.exit(0);
}

const urlList = [`${origin}/games/`, ...changed.map((slug) => `${origin}/game/${encodeURIComponent(slug)}`)];
const keyLocation = `${origin}/${key}.txt`;
const verification = await fetch(keyLocation);
if (!verification.ok || (await verification.text()).trim() !== key) throw new Error('IndexNow verification key is not live on the canonical host');

const response = await fetch('https://api.indexnow.org/indexnow', {
  method: 'POST',
  headers: { 'content-type': 'application/json; charset=utf-8' },
  body: JSON.stringify({ host: new URL(origin).host, key, keyLocation, urlList }),
});
if (![200, 202].includes(response.status)) throw new Error(`IndexNow returned HTTP ${response.status}`);

console.log(`[indexnow] changed game URLs: ${changed.length}`);
console.log(`[indexnow] submitted URLs: ${urlList.length}`);
console.log(`[indexnow] response: ${response.status}`);
