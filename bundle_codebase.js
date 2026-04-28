import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);

// ─── Exclude Rules ────────────────────────────────────────────────────────────

const SKIP_DIRS = new Set([
  'flutter', 'node_modules', '__pycache__', '.git',
  'dist', 'build', '.idea', '.gradle', '.dart_tool', 'grpc_generated',
]);

const SKIP_FILES = [
  /^\.env/,
  /^package-lock\.json$/,
  /^pnpm-lock\.yaml$/,
  /^pubspec\.lock$/,
  /^analyze_output\.txt$/,
  /^scheduler\.log$/,
  /^codebase\.txt$/,
  /^bundle_codebase\.js$/,
];

const BINARY_EXT = new Set([
  '.pyc', '.pyo',
  '.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp',
  '.mp3', '.mp4', '.wav', '.ogg',
  '.woff', '.woff2', '.ttf', '.otf', '.eot',
  '.zip', '.tar', '.gz', '.rar',
  '.jar', '.class', '.so', '.dll', '.exe',
  '.lock',
]);

// ─── Walk Directory ───────────────────────────────────────────────────────────

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (!SKIP_DIRS.has(entry.name) && !entry.name.startsWith('.')) {
        walk(path.join(dir, entry.name), files);
      }
    } else if (entry.isFile()) {
      if (!SKIP_FILES.some((re) => re.test(entry.name))) {
        files.push(path.join(dir, entry.name));
      }
    }
  }
  return files;
}

// ─── Build Output ─────────────────────────────────────────────────────────────

const ROOT   = __dirname;
const OUT    = path.join(ROOT, 'codebase.txt');
const files  = walk(ROOT).sort();
const chunks = [];
let   ok     = 0;
let   skip   = 0;

chunks.push(
  '='.repeat(80),
  '  SPEAK-SYNC — FULL CODEBASE EXPORT',
  `  Date  : ${new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}`,
  `  Total : ${files.length} files found`,
  '='.repeat(80),
);

for (const file of files) {
  const rel = path.relative(ROOT, file).replace(/\\/g, '/');
  const ext = path.extname(file).toLowerCase();
  const bar = '─'.repeat(80);

  chunks.push('', bar, `FILE: ${rel}`, bar);

  if (BINARY_EXT.has(ext)) {
    chunks.push('[binary — skipped]');
    skip++;
  } else {
    try {
      chunks.push(fs.readFileSync(file, 'utf8'));
      ok++;
    } catch (e) {
      chunks.push(`[read error: ${e.message}]`);
      skip++;
    }
  }
}

// ─── Write ────────────────────────────────────────────────────────────────────

fs.writeFileSync(OUT, chunks.join('\n'), 'utf8');

const kb = (fs.statSync(OUT).size / 1024).toFixed(1);
console.log(`\n✅  codebase.txt written`);
console.log(`    Size  : ${kb} KB`);
console.log(`    Files : ${ok} included, ${skip} skipped`);
