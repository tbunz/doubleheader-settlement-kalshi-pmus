#!/usr/bin/env python3
"""Checks the claims in README.md against the files in sources/ (or a directory you pass, e.g. one made by fetch.sh).
Usage: python3 verify.py [sources_dir]
Every check is a zero-argument function; a missing or malformed file makes that check FAIL (with the error on the
same line) rather than crashing the run, so the final ALL PASS / SOME CHECKS FAILED line is always reached.
"""
import csv, functools, hashlib, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, "sources")
IS_DEFAULT_DIR = os.path.normcase(D) == os.path.normcase(os.path.join(HERE, "sources"))
ok = True

def check(msg, fn):
    global ok
    try:
        passed, err = bool(fn()), ""
    except Exception as e:
        passed, err = False, f" ({type(e).__name__}: {e})"
    print(("PASS " if passed else "FAIL ") + msg + err); ok = ok and passed

@functools.lru_cache(maxsize=None)
def J(name): return json.load(open(os.path.join(D, name), encoding="utf-8"))
@functools.lru_cache(maxsize=None)
def B(name): return list(csv.DictReader(open(os.path.join(HERE, "bot", name), encoding="utf-8", newline="")))

# --- sources/ integrity (only when checking the committed snapshot; fresh fetches won't match) ---
if IS_DEFAULT_DIR:
    def sums():
        out = []
        for line in open(os.path.join(HERE, "SHA256SUMS"), encoding="utf-8"):
            if line.strip():
                h, name = line.split(None, 1); out.append((h.lower(), name.strip().lstrip("*")))
        return out
    def hashes_match():
        bad = [n for h, n in sums() if hashlib.sha256(open(os.path.join(D, n), "rb").read()).hexdigest() != h]
        if bad: raise AssertionError("mismatch: " + ", ".join(bad))
        return True
    try: n = len(sums())
    except Exception: n = "?"
    check(f"SHA256SUMS: all {n} source files match", hashes_match)

# --- MLB: two records, two different answers ---
def games(): return {g["gamePk"]: g for d in J("schedule_nyy_sep24-27.json")["dates"] for g in d["games"]}
def g1(): return games()[823491]
def g2(): return games()[823489]
def pr(): return open(os.path.join(D, "press_release.html"), encoding="utf-8", errors="replace").read()
check("MLB Stats API: game 1 = gamePk 823491, 4:05pm ET", lambda: g1()["doubleHeader"] == "Y" and g1()["gameNumber"] == 1 and g1()["gameDate"] == "2026-09-25T20:05:00Z")
check("MLB Stats API: game 2 = gamePk 823489, labelled 'Makeup of 9/26 PPD'", lambda: g2()["doubleHeader"] == "Y" and g2()["gameNumber"] == 2 and g2().get("description") == "Makeup of 9/26 PPD")
check("MLB Stats API: game 1 carries no makeup label", lambda: "description" not in g1())
check("MLB: game 1 Orioles 10, Yankees 2", lambda: g1()["teams"]["away"]["score"] == 10 and g1()["teams"]["home"]["score"] == 2)
check("MLB: game 2 Orioles 3, Yankees 6", lambda: g2()["teams"]["away"]["score"] == 3 and g2()["teams"]["home"]["score"] == 6)
check("Yankees press release on MLB.com: 'The New York Yankees have announced ... The game will be made up ... Friday, September 25 as the first game of a single-admission doubleheader, which will begin at 4:05 p.m.'",
      lambda: "The New York Yankees have announced that Saturday" in pr() and "The game will be made up" in pr() and "Friday, September 25 as the first game of a single-admission doubleheader, which will begin at 4:05 p.m." in pr())

# --- Kalshi: settled per the press release, and said so ---
def sat(): return J("event_KXMLBGAME-26SEP261915BALNYY.json")["event"]
def fri(): return J("event_KXMLBGAME-26SEP251905BALNYY.json")["event"]
def satm(t): return {m["ticker"]: m for m in sat()["markets"]}[t]
def frim(t): return {m["ticker"]: m for m in fri()["markets"]}[t]
check("Kalshi 'Sep 26' market rules: 'originally scheduled for Sep 26, 2026 at 7:15 PM EDT'", lambda: "originally scheduled for Sep 26, 2026 at 7:15 PM EDT" in satm("KXMLBGAME-26SEP261915BALNYY-BAL")["rules_primary"])
check("Kalshi 'Sep 26' market: result yes (Baltimore), settled 2026-09-25 22:57Z -> game 1",
      lambda: satm("KXMLBGAME-26SEP261915BALNYY-BAL")["result"] == "yes" and satm("KXMLBGAME-26SEP261915BALNYY-BAL")["settlement_ts"].startswith("2026-09-25T22:57"))
check("Kalshi 'Sep 25' market rules: 'originally scheduled for Sep 25, 2026 at 7:05 PM EDT'", lambda: "originally scheduled for Sep 25, 2026 at 7:05 PM EDT" in frim("KXMLBGAME-26SEP251905BALNYY-NYY")["rules_primary"])
check("Kalshi 'Sep 25' market: result yes (New York), settled 2026-09-26 02:33Z -> game 2",
      lambda: frim("KXMLBGAME-26SEP251905BALNYY-NYY")["result"] == "yes" and frim("KXMLBGAME-26SEP251905BALNYY-NYY")["settlement_ts"].startswith("2026-09-26T02:33"))
check("Kalshi 'Sep 26' event retitled '(Game 1)' with notice 'rescheduled as the first game of today's doubleheader'",
      lambda: sat()["title"] == "Baltimore vs New York Y (Game 1)" and "rescheduled as the first game of today" in sat()["product_metadata"]["important_info"]["markdown"])
check("Kalshi 'Sep 25' event retitled '(Game 2)' with the mirror notice",
      lambda: fri()["title"] == "Baltimore vs New York Y (Game 2)" and "rescheduled as the second game of today" in fri()["product_metadata"]["important_info"]["markdown"])
check("Kalshi settlement_sources: ESPN, Fox Sports, the Governing League", lambda: [s["name"] for s in sat()["settlement_sources"]] == ["ESPN", "Fox Sports", "the Governing League"])

# --- Polymarket US: settled per the Stats API, text never changed ---
def p25(): return J("market_aec-mlb-bal-nyy-2026-09-25.json")["market"]
def p26(): return J("market_aec-mlb-bal-nyy-2026-09-26.json")["market"]
def s25(): return J("settlement_aec-mlb-bal-nyy-2026-09-25.json")["settlement"]
def s26(): return J("settlement_aec-mlb-bal-nyy-2026-09-26.json")["settlement"]
check("PMUS: long side = Baltimore Orioles", lambda: p25()["marketSides"][0]["long"] and p25()["marketSides"][0]["team"]["name"] == "Baltimore Orioles")
check("PMUS 'Sep 25' description: 'scheduled for 2026-09-25 at 7:05PM ET ... Outcome sourced from MLB.'", lambda: "scheduled for 2026-09-25 at 7:05PM ET" in p25()["description"] and "Outcome sourced from MLB." in p25()["description"])
check("PMUS 'Sep 25' market: resolved, settlement 1 (Orioles) -> game 1", lambda: p25()["status"] == "MARKET_STATUS_RESOLVED" and s25() == 1)
check("PMUS 'Sep 26' description: 'scheduled for 2026-09-26 at 7:15PM ET'", lambda: "scheduled for 2026-09-26 at 7:15PM ET" in p26()["description"])
check("PMUS 'Sep 26' market: resolved, settlement 0 (Yankees) -> game 2", lambda: p26()["status"] == "MARKET_STATUS_RESOLVED" and s26() == 0)
check("PMUS 'Sep 26' gameStartTime is now 2026-09-25T23:30Z (a Sep 25 time on a 'Sep 26' market)", lambda: p26()["gameStartTime"] == "2026-09-25T23:30:00Z")
check("PMUS endDate = game 1 end / game 2 end", lambda: p25()["endDate"] == "2026-09-25T22:55:48Z" and p26()["endDate"] == "2026-09-26T02:28:22Z")

# --- Kalshi contract terms (needs pdftotext; skipped if absent) ---
if shutil.which("pdftotext") is None:
    print("SKIP Kalshi terms PDF checks (pdftotext not installed)")
else:
    @functools.lru_cache(maxsize=None)
    def terms():
        return re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-layout", os.path.join(D, "kalshi_BASEBALLGAMEWIN_terms.pdf"), "-"], capture_output=True, text=True, check=True).stdout)
    check("Kalshi terms: 'The Underlying can be found at: https://www.mlb.com/scores.'", lambda: "The Underlying can be found at: https://www.mlb.com/scores." in terms())
    check("Kalshi terms: designation 'through official announcements or game records ... shall control'",
          lambda: "explicitly designates which original game a makeup game represents (e.g., through official announcements or game records), that designation shall control" in terms())

# --- bot files: the pairing and the loss ---
def seen(m): return {r["market"]: r for r in B("markets_as_bot_saw_them.csv")}[m]
check("bot: paired Kalshi 'Sep 26' with Polymarket 'Sep 26' by {date, away, home}",
      lambda: all('"date": "2026-09-26"' in r["match_key"] for r in B("pairs.csv") if "26SEP26" in r["kalshi_market_id"]) and all("2026-09-26" in r["pm_market_id"] for r in B("pairs.csv") if "26SEP26" in r["kalshi_market_id"]))
check("bot: last saw PMUS 'Sep 26' gameStartTime = 2026-09-26T23:15Z at 02:27Z Sep 26 (now 2026-09-25T23:30Z)",
      lambda: seen("aec-mlb-bal-nyy-2026-09-26")["start_time_value"] == "2026-09-26T23:15:00Z" and seen("aec-mlb-bal-nyy-2026-09-26")["last_seen_utc"].startswith("2026-09-26 02:27"))
check("bot: both 'Sep 26' rules texts as first stored by the bot are identical to what the venues serve today",
      lambda: seen("aec-mlb-bal-nyy-2026-09-26")["rules_text"] == p26()["description"] and seen("KXMLBGAME-26SEP261915BALNYY-BAL")["rules_text"].startswith(satm("KXMLBGAME-26SEP261915BALNYY-BAL")["rules_primary"]))
check("bot: six two-leg trades, every leg paid 0", lambda: len(B("six_trades.csv")) == 6 and all(r["kalshi_payout"] == "0" and r["pm_payout"] == "0" for r in B("six_trades.csv")))
check("bot: realized -55.5977", lambda: abs(sum(float(r["realized_pnl_usd"]) for r in B("six_trades.csv")) + 55.5977) < 1e-6)

print("\nALL PASS" if ok else "\nSOME CHECKS FAILED"); sys.exit(0 if ok else 1)
