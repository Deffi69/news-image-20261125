// news-image-20261125 — runner for the make.fun bounty
// "Sum up 25 November's world news in one image" ($100).
//
// The entry itself is the artwork in entry.png, sitting next to
// this file: a newspaper front page for Wednesday 25 November
// 2026 with 46 stories from 7 regions — 13 of them pictured with
// original flat drawings — plus a UTC timeline, a day-in-numbers
// strip, a pinned world map, 33 one-line briefs, a DATE CHECK box
// and a verification footer.
//
// This runner's whole job is to deliver an exact copy of that
// image to the output location. It uses no network, no clock and
// no randomness, so repeated runs produce identical bytes.
//
// Node 22, standard library only.
//
// Usage:
//   node main.ts             -> writes /output/entry.png
//   node main.ts ./out       -> writes ./out/entry.png
//   node main.ts ./out/x.png -> writes ./out/x.png
// With no argument, the OUTPUT_DIR environment variable wins over
// the /output default.

import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// The artwork always lives beside this script, wherever the
// repository happens to be checked out.
const scriptFolder = dirname(fileURLToPath(import.meta.url));
const artworkPath = join(scriptFolder, "entry.png");

// Decide the final file path for the copy. A target ending in
// ".png" names the file itself; any other target is a folder and
// the copy lands inside it under the name entry.png.
function destinationFor(rawTarget) {
  const absolute = resolve(rawTarget);
  return absolute.endsWith(".png") ? absolute : join(absolute, "entry.png");
}

function sha256Hex(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function main() {
  const requested = process.argv[2] ?? process.env.OUTPUT_DIR ?? "/output";
  const destination = destinationFor(requested);

  // Read the artwork into memory first instead of copying at the
  // filesystem level: the checks below then cover the exact bytes
  // that were written, not whatever a copy call claims happened.
  // A missing entry.png means an incomplete checkout, so say that
  // plainly instead of surfacing a bare ENOENT.
  let artwork;
  try {
    artwork = readFileSync(artworkPath);
  } catch {
    throw new Error(
      `Cannot read the artwork at ${artworkPath}; ` +
        `this runner needs a complete checkout of the entry repository.`,
    );
  }
  mkdirSync(dirname(destination), { recursive: true });
  writeFileSync(destination, artwork);

  // A silently truncated copy would ship a broken entry, so the
  // run only succeeds if the copy is provably complete: matching
  // length first, then matching SHA-256.
  const writtenSize = statSync(destination).size;
  if (writtenSize !== artwork.length) {
    throw new Error(
      `Incomplete copy: ${destination} holds ${writtenSize} bytes, ` +
        `but entry.png holds ${artwork.length} bytes.`,
    );
  }

  const sourceHash = sha256Hex(artwork);
  const writtenHash = sha256Hex(readFileSync(destination));
  if (writtenHash !== sourceHash) {
    throw new Error(
      `Digest mismatch: ${destination} hashes to ${writtenHash}, ` +
        `but entry.png hashes to ${sourceHash}.`,
    );
  }

  console.log(`Wrote ${destination} (${writtenSize} bytes, sha256 ${writtenHash})`);
}

main();
