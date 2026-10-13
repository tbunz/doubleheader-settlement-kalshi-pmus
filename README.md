# One doubleheader, two venues, opposite settlements

On Sep 24, 2026 MLB moved the Saturday Sep 26 Orioles–Yankees game to Friday Sep 25, making a doubleheader. Kalshi and Polymarket US each had a "Sep 25" contract and a "Sep 26" contract on the series. Both say MLB decides. They settled the same contracts on opposite games.

| | Kalshi "Sep 26" (`KXMLBGAME-26SEP261915BALNYY`) | Polymarket US "Sep 26" (`aec-mlb-bal-nyy-2026-09-26`) |
|---|---|---|
| Contract text | "originally scheduled for Sep 26, 2026 at 7:15 PM EDT" | "scheduled for 2026-09-26 at 7:15PM ET … Outcome sourced from MLB." |
| Settled on | **game 1** (4:05pm, Orioles 10–2), at 22:57Z Sep 25 | **game 2** (the evening game, Yankees 6–3), ended 02:28Z Sep 26 |
| Told traders? | Event retitled "(Game 1)" with a notice: "This market refers to the game originally scheduled for September 26th, which has been rescheduled as the first game of today's doubleheader." | No. Text and question still say Sep 26 today; `gameStartTime` was rewritten to a Sep 25 time. |

And the "Sep 25" contracts went the other way on each venue.

Why: MLB itself has two records. Its press release says the Sep 26 game was made up "as the first game of a single-admission doubleheader, which will begin at 4:05 p.m." Its Stats API labels **game 2** as "Makeup of 9/26 PPD". Kalshi's settlement matches the announcement; Polymarket US's matches the data feed. Kalshi's filed contract terms say the governing body's designation controls "through official announcements or game records" — the two things that disagreed.

An arbitrage bot that paired the contracts by `{date, away, home}` traded both pairs during game 1 and lost both legs of all six trades (−$55.60).

## Check it yourself

```
python3 verify.py            # checks every claim above against sources/ (the responses captured 2026-10-13)
./fetch.sh && python3 verify.py sources_fresh   # re-fetch from Kalshi, Polymarket US and MLB right now, then check those
```

No API keys needed. `pdftotext` (poppler) is needed for the two contract-terms checks; they're skipped without it.

## What's here

`sources/` — raw public responses with response headers, hashed in `SHA256SUMS`:

| file | what |
|---|---|
| `event_KXMLBGAME-26SEP261915BALNYY.json`, `…26SEP251905….json` | Kalshi event objects: title, notice, settlement sources, and both markets with rules text, result, settlement time |
| `market_aec-mlb-bal-nyy-2026-09-2[56].json`, `settlement_….json` | Polymarket US market objects (description, question, gameStartTime, endDate) and settlement values |
| `schedule_nyy_sep24-27.json` | MLB Stats API: both games with scores, linescores, game numbers, the "Makeup of 9/26 PPD" label |
| `press_release.html` | MLB's Sep 24 announcement |
| `kalshi_BASEBALLGAMEWIN_terms.pdf` | Kalshi's CFTC-filed contract terms for this market type |

`bot/` — five small extracts from the bot's database, included so the trade and what the bot saw are on the record:

| file | what |
|---|---|
| `pairs.csv` | the four pairings and the match key |
| `markets_as_bot_saw_them.csv` | the six markets' text and start-time fields as last stored by the bot, with first/last-seen times |
| `six_trades.csv` | the six trades, both legs, venue order IDs, payouts |
| `settlement_timeline.csv` | when the bot's reconciler saw each leg settle, and the verdict |
| `pm_sibling_text_transitions.txt` | Polymarket US's "Sep 26" sibling markets changed which game their text named twice during Sep 25 (280 markets; per-market record available on request) |

## What this does not show

Which MLB record each venue actually used — neither publishes that; "consistent with" is the right phrasing. When Kalshi added its event notice (no timestamp is exposed). Why Polymarket US's reference data moved during the day. The full bot database and journal, and ~750 sibling markets' snapshots, exist and are available on request.
