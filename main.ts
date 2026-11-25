// news-image-20261125 — entry runner for the make.fun bounty
// "Sum up 25 November's world news in one image" ($100).
//
// The artwork for this entry is the file entry.png next to this
// script: a dense newspaper front page for Wednesday 25 November
// 2026 — 46 stories across 7 regions, 13 of them pictured with
// original flat drawings, plus a UTC timeline, a day-in-numbers
// strip, a pinned world map, 33 one-line briefs, a DATE CHECK box
// and a verification footer.
//
// All this program does is place an exact copy of that image at
// the output location. It never touches the network, never reads
// the clock, and never rolls any dice, so running it twice in a
// row produces the same bytes every time.
//
// Node 22, standard library only.
//
// How to run it:
//   node main.ts             -> writes /output/entry.png
//   node main.ts ./out       -> writes ./out/entry.png
//   node main.ts ./out/x.png -> writes ./out/x.png
// The OUTPUT_DIR environment variable is used when no argument
// is given.

import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// The image lives beside this script, wherever the repo is checked out.
const scriptDir = dirname(fileURLToPath(import.meta.url));
const entryPath = join(scriptDir, "entry.png");

// Work out where the copy should land. A path ending in ".png" is
// taken as the file itself; anything else is taken as a folder
// that will hold a file called entry.png.
function outputFor(rawTarget) {
  const target = resolve(rawTarget);
  return target.endsWith(".png") ? target : join(target, "entry.png");
}

const rawTarget = process.argv[2] ?? process.env.OUTPUT_DIR ?? "/output";
const destination = outputFor(rawTarget);

// Read the artwork once, then write those exact bytes out. Reading
// first (instead of a filesystem copy) means the digest check below
// compares the bytes we actually wrote against the bytes we read.
const artwork = readFileSync(entryPath);
mkdirSync(dirname(destination), { recursive: true });
writeFileSync(destination, artwork);

// A quiet truncation would ship a broken entry, so refuse to
// finish unless the copy is complete: same length, same SHA-256.
const writtenSize = statSync(destination).size;
if (writtenSize !== artwork.length) {
  throw new Error(
    `Incomplete copy: ${destination} holds ${writtenSize} bytes, ` +
      `but entry.png holds ${artwork.length} bytes.`,
  );
}

const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const sourceHash = sha256(artwork);
const writtenHash = sha256(readFileSync(destination));
if (writtenHash !== sourceHash) {
  throw new Error(
    `Digest mismatch: ${destination} hashes to ${writtenHash}, ` +
      `but entry.png hashes to ${sourceHash}.`,
  );
}

console.log(`Wrote ${destination} (${writtenSize} bytes, sha256 ${writtenHash})`);
