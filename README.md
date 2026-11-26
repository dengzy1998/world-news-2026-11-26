# The World Today — Thursday 26 November 2026

One image summing up 26 November 2026's world news: 52 sourced stories
across 5 regions — 3 illustrated leads, 12 grid cards, 37 one-liners — plus
a UTC timeline, a numbered schematic map, and a DATE CHECK box listing
older stories deliberately left out.

Entry for the make.fun bounty
[news-image-20261126](https://make.fun/bounty/news-image-20261126).

[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/dengzy1998/world-news-2026-11-26/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/dengzy1998/world-news-2026-11-26/reward.svg)](https://make.fun/bounty/news-image-20261126)

## How it is built

`render_poster.py` draws `entry.png` (1024×1024, Pillow, deterministic)
from the story ledger in `../stories.md`. `main.py` (standard library only)
copies that finished image to `$MAKEFUN_OUTPUT_DIR/entry.png`, so both
grading runs produce byte-identical output.

## Sources

Reuters, Associated Press, South China Morning Post, Japan Times,
Al Jazeera, Economic Times, BBC, Sky Sports — see `../stories.md` for the
per-story ledger.
