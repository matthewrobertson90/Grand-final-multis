# Grand Final Multi Tracker

A single-page live tracker for three AFL Grand Final multis (Fremantle v Brisbane Lions). Open `index.html` (GitHub Pages build of `app.html`, made by `tools/build_pages.sh`) and, during the game, tap in scores, disposals and goals. The page shows each leg's live chance, each multi's correlated chance (20,000 simulated finishes), fair value, near-miss odds, a cheer list and a trend chart.

Model: each player's pre-game average acts as a gamma prior, updated with the in-game count; the chance of the remaining count clearing the line comes from the resulting negative binomial. The final margin is modelled as normal, and one shared "who's on top" factor links the margin to every player's output. All settings can be changed on the Model tab.

## Live feed

`tools/poll.py` polls the official AFL match centre API (`api.afl.com.au`, match `CD_M20260142901`) about every 20 seconds and writes `data/live.json` when something changes. A Claude session relays each snapshot into the published page's database (`live/gf`), and the page picks it up in real time. Untick "Use live stats" in the page to go back to tapping stats in by hand.

## Research

`tools/research.py` pulls every 2026 Brisbane and Fremantle match from the same API and computes each player's season average, last-five average and game-to-game spread (`data/research.json`). The model's expected counts are 60% season and 40% last five. The Lions' 57% pre-game chance is Squiggle's betting-market model.
