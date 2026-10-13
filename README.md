# One doubleheader, two venues, opposite settlements

On Sep 24, 2026 the Saturday Sep 26 Orioles–Yankees game was moved to Friday Sep 25, making a doubleheader. Kalshi and Polymarket US each had a "Sep 25" contract and a "Sep 26" contract on the series. They settled the same contracts on opposite games.

| | Kalshi "Sep 26" (`KXMLBGAME-26SEP261915BALNYY`) | Polymarket US "Sep 26" (`aec-mlb-bal-nyy-2026-09-26`) |
|---|---|---|
| Contract text | "originally scheduled for Sep 26, 2026 at 7:15 PM EDT" | "scheduled for 2026-09-26 at 7:15PM ET … Outcome sourced from MLB." |
| Settled on | **game 1** (scheduled 4:05pm, Orioles 10–2); settled 22:57Z Sep 25 | **game 2** (the second game, Yankees 6–3); market `endDate` 02:28Z Sep 26 |

## Two records, two answers

A Yankees press release on MLB.com and MLB's own Stats API disagree on which game of the doubleheader was the Sep 26 makeup:

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

Kalshi's "Sep 26" settlement matches the press release, and Polymarket US's matches the Stats API. That match is all this shows. I don't know which source either venue actually settled from — one of these two records, or something else entirely — and neither venue's API response says.

## The point

When they were listed, both "Sep 26" contracts pointed at the same game: Orioles at Yankees, Sep 26, 7:15pm ET. Then that game was moved into a Sep 25 doubleheader, and the Yankees' announcement and MLB's Stats API disagree about which of the two games it became. Both contracts' rules text reads today exactly as it did when the bot first saw them, but they settled on different games: Kalshi's on game 1, Polymarket US's on game 2. (Kalshi's event now carries a "(Game 1)" title and notice; Polymarket US's `gameStartTime` now reads `2026-09-25T23:30:00Z`. Neither API shows when those changed.)

Each venue's settlement lines up with one of those two records, so neither is plainly wrong, and they still paid out on different games. Two contracts can say the same thing, name the same authority, and still not be the same bet.

How the two "Sep 26" contracts identify their game:

| | Kalshi | Polymarket US |
|---|---|---|
| ID | `KXMLBGAME-26SEP261915BALNYY`: `26SEP26` = 2026-09-26, `1915` = 7:15pm, BAL, NYY | `aec-mlb-bal-nyy-2026-09-26`: BAL, NYY, 2026-09-26 (no time) |
| Rules text | "Baltimore vs New York Y professional baseball game originally scheduled for Sep 26, 2026 at 7:15 PM EDT" | "Baltimore Orioles vs New York Yankees MLB game scheduled for 2026-09-26 at 7:15PM ET" |
| Other field | — | `question`: "scheduled for September 26, 2026 at 11:15 PM UTC" (= 7:15pm EDT) |
| Away/home | — | `marketSides`: Orioles `away`, Yankees `home` |

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
