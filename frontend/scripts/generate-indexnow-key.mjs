import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const key = process.env.INDEXNOW_KEY?.trim();
if (!key) process.exit(0);
if (!/^[A-Za-z0-9-]{8,128}$/.test(key)) throw new Error('INDEXNOW_KEY must be 8-128 letters, numbers, or dashes');

const here = path.dirname(fileURLToPath(import.meta.url));
await writeFile(path.resolve(here, '../../static', `${key}.txt`), key);
console.log('[indexnow] verification key file generated');
