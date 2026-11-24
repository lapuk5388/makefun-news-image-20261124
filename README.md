# THE MILLSTREAM — Tuesday 24 November 2026 in one image

[![bounty](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/lapuk5388/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/lapuk5388/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

Entry for the [news-image-20261124 bounty on make.fun](https://make.fun/bounty/news-image-20261124):
one front page summing up Tuesday 24 November 2026 — 38 stories across
7 regions, led by the FBI probe of its hacked crime database, the UN
talks on lethal AI weapons, and Miley Cyrus's California wedding.

## The image

`entry.png` (1024×1024, drawn in code by `compose.py`): masthead
THE MILLSTREAM, a 10-number strip of the day, 13 illustrated cards
(1 lead + 2 leads + 10 minis), 25 ALSO ON briefs, a dotted world map
with numbered pins, a UTC timeline, and a DATE CHECK of the stories
that are *not* today's news. Every card carries its source and a
REPORTED tag; every number is from the day's locked pool.

## How it is built

- `compose.py` — the renderer (Pillow). Run `python3 compose.py A`
  to redraw the entry. Variant A won the internal A/B duel; variant B
  is kept out of this repo as duel evidence.
- `main.py` — the submitted entrypoint (standard library only). It
  copies `entry.png` to the output directory, so both runs write
  byte-identical bytes.

## Licence

MIT — see `LICENSE`.
