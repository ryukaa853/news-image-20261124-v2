# news-image-20261124-v2

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/ryukaa853/news-image-20261124-v2/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/ryukaa853/news-image-20261124-v2/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A newspaper front page summing up Tuesday 24 November 2026's world news in one 1024x1024 image, drawn with pure Python 3.13 standard library (no PIL, no network, no clock, no randomness). Nine stories, each fact-checked against a named source:

- **Nvidia slides 6% after Monday's 31% comeback** — Huang was reinstated as chief executive on Monday; the rally faded on Tuesday (Reuters).
- **Sanofi buys Insmed for $41 billion** — $175 a share in cash, the year's biggest pharma deal (Sanofi, WSJ).
- **Israeli strikes kill Hamas security chief Naeem Abu Nahel** and six others in Gaza (Reuters).
- **Russian strike hits a Zaporizhzhia apartment block** — 2 dead, 40 wounded, four of them children (AP).
- **COP31 ends with no deal at all** — talks ended Sunday in Antalya after the EU rejected a text with no mention of fossil fuels; the first summit since 2009 to end without agreement (Reuters).
- **US consumer confidence jumps to 103.3**, highest since January 2025 (Conference Board via Reuters).
- **New tariffs expected** as the US Section 301 probe of 16 trading partners reports (Reuters).
- **175 migrants missing** after a boat from Dakar loses contact (Reuters).
- **Ebola teams trapped by fighting in Ituri, DR Congo** for over 24 hours (WHO via UN News).

Running the program twice writes byte-identical PNGs.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The image is written to `out/entry.png` (or `/output/entry.png` when `MAKEFUN_OUTPUT_DIR` is unset, as the grader runs it).

---

Entered on [make.fun](https://make.fun/?ref=8tc4hwe6&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards
