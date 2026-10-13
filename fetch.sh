#!/usr/bin/env bash
# Re-fetches every public source in sources/ from its origin. No API keys. ~8 requests.
# Usage: ./fetch.sh [outdir]   (default: sources_fresh/)
set -euo pipefail
OUT="${1:-sources_fresh}"; mkdir -p "$OUT"
get () { echo "GET $2"; curl -sS -L -D "$OUT/$1.headers" -o "$OUT/$1" -A "Mozilla/5.0" "$2"; }

K="https://api.elections.kalshi.com/trade-api/v2"
get event_KXMLBGAME-26SEP261915BALNYY.json "$K/events/KXMLBGAME-26SEP261915BALNYY?with_nested_markets=true"
get event_KXMLBGAME-26SEP251905BALNYY.json "$K/events/KXMLBGAME-26SEP251905BALNYY?with_nested_markets=true"

P="https://gateway.polymarket.us/v1"
for s in aec-mlb-bal-nyy-2026-09-25 aec-mlb-bal-nyy-2026-09-26; do
  get market_$s.json     "$P/market/slug/$s"
  get settlement_$s.json "$P/markets/$s/settlement"
done

get schedule_nyy_sep24-27.json "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-09-24&endDate=2026-09-27&teamId=147&hydrate=linescore,game(content(summary)),decisions"
get press_release.html "https://www.mlb.com/press-release/saturday-s-yankees-orioles-game-saturday-september-26-rescheduled-due-to-the-forecast-of-sustained-inclement-weather"
get kalshi_BASEBALLGAMEWIN_terms.pdf "https://assets.kalshi.com/contract_terms/BASEBALLGAMEWIN.pdf"

( cd "$OUT" && sha256sum * > ../SHA256SUMS.fresh )
echo; echo "Fetched to $OUT/. Now: python3 verify.py $OUT"
