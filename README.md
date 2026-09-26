# Grand Final Multi Tracker

A single-page live tracker for three AFL Grand Final multis (Fremantle v Brisbane Lions). Open `index.html` and, during the game, tap in scores, disposals and goals. The page shows each leg's live chance, each multi's correlated chance (20,000 simulated finishes), fair value, near-miss odds, a cheer list and a trend chart.

Model: each player's pre-game average acts as a gamma prior, updated with the in-game count; the chance of the remaining count clearing the line comes from the resulting negative binomial. The final margin is modelled as normal, and one shared "who's on top" factor links the margin to every player's output. All settings can be changed on the Model tab.
