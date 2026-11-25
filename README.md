# news-image-20261125 — World News in One Image

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Deffi69/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Deffi69/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

Entry for the make.fun bounty **"Sum up 25 November's world news in one image"**:
https://make.fun/bounty/news-image-20261125

A dense newspaper front page (1024×1024) of Wednesday 25 November 2026: 46 stories
across 7 regions — 3 big leads (Shenzhou-24 carries the first Pakistani into
orbit, Zelenskiy confirms the Baltic ship strike, Asian stocks tumble on tariff
threats) plus 10 pictured cards, each with an original flat illustration, a
factual 6–12-word headline, a number-dense deck and a source with a
CLAIM/CONFIRMED label. Also on the page: a UTC timeline, a day-in-numbers
strip, a world map with pins matching the 13 pictured stories, 33 one-line
briefs, a DATE CHECK box and a date-verification footer. Every story happened
or was first reported on 25 November 2026.

## How it works

`main.ts` (Node 22, standard library only) copies the committed `entry.png`
byte-for-byte to `/output/entry.png`. No network, no randomness — two runs
always write identical bytes.

```sh
node main.ts            # writes /output/entry.png
node main.ts ./out      # writes ./out/entry.png
```
