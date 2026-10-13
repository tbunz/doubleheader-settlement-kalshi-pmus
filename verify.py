#!/usr/bin/env python3
"""Checks the claims in README.md against the files in sources/ (or a directory you pass, e.g. one made by fetch.sh).
Usage: python3 verify.py [sources_dir]
"""
import csv, json, os, re, subprocess, sys

D = sys.argv[1] if len(sys.argv) > 1 else "sources"
ok = True
def check(cond, msg):
    global ok
    print(("PASS " if cond else "FAIL ") + msg); ok = ok and bool(cond)
def J(name): return json.load(open(os.path.join(D, name)))

# --- MLB: two records, two different answers ---
games = {g["gamePk"]: g for d in J("schedule_nyy_sep24-27.json")["dates"] for g in d["games"]}
g1, g2 = games[823491], games[823489]
check(g1["doubleHeader"] == "Y" and g1["gameNumber"] == 1 and g1["gameDate"] == "2026-09-25T20:05:00Z", "MLB Stats API: game 1 = gamePk 823491, 4:05pm ET")
check(g2["doubleHeader"] == "Y" and g2["gameNumber"] == 2 and g2.get("description") == "Makeup of 9/26 PPD", "MLB Stats API: game 2 = gamePk 823489, labelled 'Makeup of 9/26 PPD'")
check("description" not in g1, "MLB Stats API: game 1 carries no makeup label")
check(g1["teams"]["away"]["score"] == 10 and g1["teams"]["home"]["score"] == 2, "MLB: game 1 Orioles 10, Yankees 2")
check(g2["teams"]["away"]["score"] == 3 and g2["teams"]["home"]["score"] == 6, "MLB: game 2 Orioles 3, Yankees 6")
pr = open(os.path.join(D, "press_release.html"), encoding="utf-8", errors="replace").read()
check("The game will be made up" in pr and "Friday, September 25 as the first game of a single-admission doubleheader, which will begin at 4:05 p.m." in pr,
      "MLB press release: 'The game will be made up ... Friday, September 25 as the first game of a single-admission doubleheader, which will begin at 4:05 p.m.'")

# --- Kalshi: settled per the press release, and said so ---
sat = J("event_KXMLBGAME-26SEP261915BALNYY.json")["event"]; fri = J("event_KXMLBGAME-26SEP251905BALNYY.json")["event"]
satm = {m["ticker"]: m for m in sat["markets"]}; frim = {m["ticker"]: m for m in fri["markets"]}
check("originally scheduled for Sep 26, 2026 at 7:15 PM EDT" in satm["KXMLBGAME-26SEP261915BALNYY-BAL"]["rules_primary"], "Kalshi 'Sep 26' market rules: 'originally scheduled for Sep 26, 2026 at 7:15 PM EDT'")
check(satm["KXMLBGAME-26SEP261915BALNYY-BAL"]["result"] == "yes" and satm["KXMLBGAME-26SEP261915BALNYY-BAL"]["settlement_ts"].startswith("2026-09-25T22:57"),
      "Kalshi 'Sep 26' market: result yes (Baltimore), settled 2026-09-25 22:57Z -> game 1")
check("originally scheduled for Sep 25, 2026 at 7:05 PM EDT" in frim["KXMLBGAME-26SEP251905BALNYY-NYY"]["rules_primary"], "Kalshi 'Sep 25' market rules: 'originally scheduled for Sep 25, 2026 at 7:05 PM EDT'")
check(frim["KXMLBGAME-26SEP251905BALNYY-NYY"]["result"] == "yes" and frim["KXMLBGAME-26SEP251905BALNYY-NYY"]["settlement_ts"].startswith("2026-09-26T02:33"),
      "Kalshi 'Sep 25' market: result yes (New York), settled 2026-09-26 02:33Z -> game 2")
check(sat["title"] == "Baltimore vs New York Y (Game 1)" and "rescheduled as the first game of today" in sat["product_metadata"]["important_info"]["markdown"],
      "Kalshi 'Sep 26' event retitled '(Game 1)' with notice 'rescheduled as the first game of today's doubleheader'")
check(fri["title"] == "Baltimore vs New York Y (Game 2)" and "rescheduled as the second game of today" in fri["product_metadata"]["important_info"]["markdown"],
      "Kalshi 'Sep 25' event retitled '(Game 2)' with the mirror notice")
check([s["name"] for s in sat["settlement_sources"]] == ["ESPN", "Fox Sports", "the Governing League"], "Kalshi settlement_sources: ESPN, Fox Sports, the Governing League")

# --- Polymarket US: settled per the Stats API, text never changed ---
p25 = J("market_aec-mlb-bal-nyy-2026-09-25.json")["market"]; p26 = J("market_aec-mlb-bal-nyy-2026-09-26.json")["market"]
s25 = J("settlement_aec-mlb-bal-nyy-2026-09-25.json")["settlement"]; s26 = J("settlement_aec-mlb-bal-nyy-2026-09-26.json")["settlement"]
check(p25["marketSides"][0]["long"] and p25["marketSides"][0]["team"]["name"] == "Baltimore Orioles", "PMUS: long side = Baltimore Orioles")
check("scheduled for 2026-09-25 at 7:05PM ET" in p25["description"] and "Outcome sourced from MLB." in p25["description"], "PMUS 'Sep 25' description: 'scheduled for 2026-09-25 at 7:05PM ET ... Outcome sourced from MLB.'")
check(p25["status"] == "MARKET_STATUS_RESOLVED" and s25 == 1, "PMUS 'Sep 25' market: resolved, settlement 1 (Orioles) -> game 1")
check("scheduled for 2026-09-26 at 7:15PM ET" in p26["description"], "PMUS 'Sep 26' description: 'scheduled for 2026-09-26 at 7:15PM ET'")
check(p26["status"] == "MARKET_STATUS_RESOLVED" and s26 == 0, "PMUS 'Sep 26' market: resolved, settlement 0 (Yankees) -> game 2")
check(p26["gameStartTime"] == "2026-09-25T23:30:00Z", "PMUS 'Sep 26' gameStartTime is now 2026-09-25T23:30Z (a Sep 25 time on a 'Sep 26' market)")
check(p25["endDate"] == "2026-09-25T22:55:48Z" and p26["endDate"] == "2026-09-26T02:28:22Z", "PMUS endDate = game 1 end / game 2 end")

# --- Kalshi contract terms (needs pdftotext; skipped if absent) ---
try:
    txt = re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-layout", os.path.join(D, "kalshi_BASEBALLGAMEWIN_terms.pdf"), "-"], capture_output=True, text=True, check=True).stdout)
    check("The Underlying can be found at: https://www.mlb.com/scores." in txt, "Kalshi terms: 'The Underlying can be found at: https://www.mlb.com/scores.'")
    check("explicitly designates which original game a makeup game represents (e.g., through official announcements or game records), that designation shall control" in txt,
          "Kalshi terms: designation 'through official announcements or game records ... shall control'")
except (FileNotFoundError, subprocess.CalledProcessError):
    print("SKIP Kalshi terms PDF checks (pdftotext not installed)")

# --- bot files: the pairing and the loss ---
pairs = list(csv.DictReader(open("bot/pairs.csv")))
check(all('"date": "2026-09-26"' in r["match_key"] for r in pairs if "26SEP26" in r["kalshi_market_id"]) and all("2026-09-26" in r["pm_market_id"] for r in pairs if "26SEP26" in r["kalshi_market_id"]),
      "bot: paired Kalshi 'Sep 26' with Polymarket 'Sep 26' by {date, away, home}")
seen = {r["market"]: r for r in csv.DictReader(open("bot/markets_as_bot_saw_them.csv"))}
check(seen["aec-mlb-bal-nyy-2026-09-26"]["start_time_value"] == "2026-09-26T23:15:00Z" and seen["aec-mlb-bal-nyy-2026-09-26"]["last_seen_utc"].startswith("2026-09-26 02:27"),
      "bot: last saw PMUS 'Sep 26' gameStartTime = 2026-09-26T23:15Z at 02:27Z Sep 26 (now 2026-09-25T23:30Z)")
trades = list(csv.DictReader(open("bot/six_trades.csv")))
check(len(trades) == 6 and all(r["kalshi_payout"] == "0" and r["pm_payout"] == "0" for r in trades), "bot: six two-leg trades, every leg paid 0")
check(abs(sum(float(r["realized_pnl_usd"]) for r in trades) + 55.5977) < 1e-6, "bot: realized -55.5977")

print("\nALL PASS" if ok else "\nSOME CHECKS FAILED"); sys.exit(0 if ok else 1)
