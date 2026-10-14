# Same contract, different games

**TLDR**

- Kalshi and Polymarket US each listed a contract on the Orioles–Yankees game scheduled for Sep 26, 2026 at 7:15pm ET. When they were listed, both named the same game.
- The game was rescheduled and moved into a Sep 25 doubleheader. MLB.com carried two records that disagree on which game of the doubleheader it became: a Yankees press release says game 1, and MLB's Stats API labels game 2 as the Sep 26 makeup.
- Kalshi settled its contract on game 1 (Orioles won). Polymarket US settled on game 2 (Yankees won).
- Each settlement matches a record published on MLB.com, a source both venues name, so each is defensible.

| | Kalshi (`KXMLBGAME-26SEP261915BALNYY`) | Polymarket US (`aec-mlb-bal-nyy-2026-09-26`) |
|---|---|---|
| Contract text | "originally scheduled for Sep 26, 2026 at 7:15 PM EDT"\* | "scheduled for 2026-09-26 at 7:15PM ET … Outcome sourced from MLB." |
| Settled on | **game 1** (Orioles 10–2) | **game 2** (Yankees 6–3) |
| Settled | 22:57Z Sep 25 | market `endDate` 02:28Z Sep 26 |
| Matches | Yankees press release on MLB.com: "made up … as the first game" | MLB Stats API: game 2 is "Makeup of 9/26 PPD" |

\* "Originally" is Kalshi's standard wording for every game market, not an edit made after the move. Its Sep 25 contract, which was never rescheduled, also reads "originally scheduled for Sep 25, 2026 at 7:05 PM EDT".

## Two records, two answers

MLB.com carries two records that disagree on which game of the doubleheader was the Sep 26 makeup:

- **Yankees press release on MLB.com** (published Sep 24): "The New York Yankees have announced that Saturday's Yankees-Orioles game (Saturday, September 26) will not be played … The game will be made up tomorrow, Friday, September 25 as the first game of a single-admission doubleheader, which will begin at 4:05 p.m."
- **MLB Stats API** (schedule endpoint, fetched Oct 13): game 2 (`gamePk` 823489) carries `"description": "Makeup of 9/26 PPD"`. Game 1 (`gamePk` 823491) has no makeup label.

Both venues name MLB as a resolution source:

- **Kalshi**'s contract terms (`BASEBALLGAMEWIN`): "The Source Agencies are, in hierarchical order, the governing league or association of &lt;baseball game&gt; (e.g., Major League Baseball, …), ESPN, CBS Sports, Fox Sports, the Associated Press, The Wall Street Journal, and the official broadcaster of &lt;baseball game&gt;."
- **Polymarket US**'s market description: "Outcome sourced from MLB."

Kalshi's settlement matches the press release, and a notice on its event says the game "has been rescheduled as the first game of today’s doubleheader." Polymarket US's settlement matches the Stats API. Neither venue says which record it settled from, so I'm not claiming either one used these exact sources. Only that each settlement squares with a record published on MLB.com, and that is what makes each one defensible.

## The point

Two contracts that named the same game by date, time and teams ended up as bets on different games when the underlying reality changed. Even an event as simple as a baseball game can be complex to resolve as an event contract.

## How this showed up

I was running a cross-venue arbitrage experiment that paired these contracts by date and teams, and took a loss on both pairs: six trades on Sep 25, both legs lost on every one, −$55.60 in total.

`bot/` holds five small extracts from the experiment's database so the pairing, the trades, and what the bot saw are on the record.

## What's here

`sources/`: raw public responses with response headers, hashed in `SHA256SUMS`:

| file | what |
|---|---|
| `event_KXMLBGAME-26SEP261915BALNYY.json`, `…26SEP251905….json` | Kalshi event objects: title, notice, settlement sources, and both markets with rules text, result, settlement time |
| `market_aec-mlb-bal-nyy-2026-09-2[56].json`, `settlement_….json` | Polymarket US market objects (description, question, gameStartTime, endDate) and settlement values |
| `schedule_nyy_sep24-27.json` | MLB Stats API: both games with scores, linescores, game numbers, the "Makeup of 9/26 PPD" label |
| `press_release.html` | the Yankees' Sep 24 press release, as published on MLB.com |
| `kalshi_BASEBALLGAMEWIN_terms.pdf` | Kalshi's contract terms for this market type |

`bot/`:

| file | what |
|---|---|
| `pairs.csv` | the four pairings and the match key |
| `markets_as_bot_saw_them.csv` | the six markets' text and start-time fields as last stored by the bot, with first/last-seen times |
| `six_trades.csv` | the six trades, both legs, venue order IDs, payouts |
| `settlement_timeline.csv` | when the bot's reconciler saw each leg settle, and the verdict |
| `pm_sibling_text_transitions.txt` | Polymarket US's other "Sep 26" markets on this game (280 of them) changed the date and time their text named during Sep 25, ending at Sep 26 7:15PM ET; counts per transition (per-market record available on request) |

## Check it yourself

```
python3 verify.py                               # checks the core claims against sources/ (responses captured 2026-10-13)
./fetch.sh && python3 verify.py sources_fresh   # re-fetch from Kalshi, Polymarket US and MLB right now, then check those
```

No API keys needed. `pdftotext` (poppler) is needed for the two contract-terms checks; they're skipped without it.
