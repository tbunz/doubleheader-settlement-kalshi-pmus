# One doubleheader, two venues, opposite settlements

**TLDR**

- Kalshi and Polymarket US each listed a contract on the Sep 25 Orioles–Yankees game and one on the Sep 26 game, naming the same dates and times.
- The Sep 26 game was rescheduled to Sep 25 as part of a doubleheader. A Yankees press release says it became the first game; MLB's Stats API labels the second game as the Sep 26 makeup.
- Each venue mapped its "Sep 26" contract to a different game of the doubleheader: Kalshi to game 1, Polymarket US to game 2.
- The contract text never changed on either venue, but the two "Sep 26" contracts paid out on different winners.

| | Kalshi "Sep 26" (`KXMLBGAME-26SEP261915BALNYY`) | Polymarket US "Sep 26" (`aec-mlb-bal-nyy-2026-09-26`) |
|---|---|---|
| Contract text | "originally scheduled for Sep 26, 2026 at 7:15 PM EDT"\* | "scheduled for 2026-09-26 at 7:15PM ET … Outcome sourced from MLB." |
| Settled on | **game 1** (scheduled 4:05pm, Orioles 10–2); settled 22:57Z Sep 25 | **game 2** (the second game, Yankees 6–3); market `endDate` 02:28Z Sep 26 |

\* "Originally" is Kalshi's standard wording for every game market, not an edit made after the move. The Sep 25 contract, which was never rescheduled, also reads "originally scheduled for Sep 25, 2026 at 7:05 PM EDT".

## Two records, two answers

A Yankees press release on MLB.com and MLB's own Stats API *disagree* on which game of the doubleheader was the Sep 26 makeup:

- **Yankees press release on MLB.com** (published Sep 24): "The New York Yankees have announced that Saturday's Yankees-Orioles game (Saturday, September 26) will not be played … The game will be made up tomorrow, Friday, September 25 as the first game of a single-admission doubleheader, which will begin at 4:05 p.m."
- **MLB Stats API** (schedule endpoint, fetched Oct 13): game 2 (`gamePk` 823489) carries `"description": "Makeup of 9/26 PPD"`. Game 1 (`gamePk` 823491) has no makeup label.

What each venue names as its resolution source, verbatim:

**Kalshi**, event `settlement_sources`:

```json
[{"name":"ESPN","url":"https://www.espn.com"},{"name":"Fox Sports","url":"https://www.foxsports.com"},{"name":"the Governing League","url":"https://www.mlb.com/"}]
```

Kalshi's contract terms, `BASEBALLGAMEWIN`:

> Source Agency: The Source Agencies are, in hierarchical order, the governing league or association of &lt;baseball game&gt; (e.g., Major League Baseball, NCAA, Nippon Professional Baseball, or the World Baseball Classic organizing body), ESPN, CBS Sports, Fox Sports, the Associated Press, The Wall Street Journal, and the official broadcaster of &lt;baseball game&gt;.

**Polymarket US**, market `description`:

> Outcome sourced from MLB.

Kalshi's "Sep 26" settlement matches the press release, and Polymarket US's matches the Stats API. I am *not* claiming that either venue resolved exactly to those sources. Neither venue says exactly which record it settled from, and nothing in either API response shows its reasoning. What the match does show is that each settlement can be squared with a record published on MLB.com, and MLB is the source both venues name.

*Each venue made a defensible decision about how to re-map the rescheduled game.*

## The point

When they were listed, both "Sep 26" contracts named the same game: Orioles at Yankees, Sep 26, 7:15pm ET. Then:

- The game was moved into a Sep 25 doubleheader, and the Yankees' announcement and MLB's Stats API disagree about which of the two games it became.
- Neither venue changed its rules text. Both contracts read today exactly as they did when the bot first saw them.
- Other fields did change. Kalshi's event now carries a "(Game 1)" title and a notice; Polymarket US's `gameStartTime` now reads `2026-09-25T23:30:00Z`. Neither API shows when. The bot last saw Polymarket US's `gameStartTime` still reading Sep 26 at 02:27Z Sep 26, about a minute before the market's `endDate`.
- The two contracts settled on different games: Kalshi's on game 1, Polymarket US's on game 2.

Each venue's settlement lines up with one of the two records, so neither is plainly wrong. But two contracts that name the same game by date, time and teams were not the same bet.

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
