"""
Claude Trading Assistant — Nifty 50 opening-range breakout helper (educational).
by Orbynex · https://manageme.orbynex.io/ · WhatsApp 7012937250

Four jobs, one command:
  1. SCAN  — Nifty 50 stocks whose price broke the 9:15–9:45 opening range
  2. PLAN  — entry, stop (other side of the range, capped by --max-stop-pct), target (--rr x risk)
  3. SIZE  — how many shares so that hitting the stop loses only --risk-pct of --capital
  4. TEST  — 10,000 replays of the rest of the session, built from this stock's own recent
             5-minute moves: how often the target is hit first, how often the stop is hit first

  python assistant.py --capital 100000 --risk-pct 1
  python assistant.py --capital 100000 --risk-pct 1 --date 2026-11-13 --lang ml

NOT FINANCIAL ADVICE. A learning / research tool. It does not tell you to buy or sell anything.
Free Yahoo Finance data is delayed (about 15 min) and 5-minute history covers only ~60 days.
Replays are a statistical model of the past, not a prediction. Trading involves risk of loss.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import sys
from datetime import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import yfinance as yf

HERE = Path(__file__).resolve().parent
NSE_LIST = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
OR_START, OR_END, CLOSE_BY = time(9, 15), time(9, 45), time(15, 20)
DISCLAIMER = ("NOT FINANCIAL ADVICE. Educational tool only. Delayed free data; replays model the past, "
              "they do not predict the future. Trading involves risk of loss. Do your own research.")
DISCLAIMER_ML = ("ഇത് financial advice അല്ല. പഠിക്കാനുള്ള tool മാത്രം. Free data വൈകിയാണ് വരിക; replays "
                 "പഴയ data-യുടെ model ആണ്, ഭാവി പ്രവചിക്കില്ല. Trading-ൽ നഷ്ടം വരാം.")


def nifty50_symbols() -> list[str]:
    """Official list from NSE; falls back to the bundled copy if NSE is unreachable."""
    try:
        r = requests.get(NSE_LIST, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        syms = [s.strip() for s in df["Symbol"].tolist()]
        (HERE / "nifty50.txt").write_text("\n".join(syms) + "\n", encoding="utf-8")
        return syms
    except Exception:
        return [s.strip() for s in (HERE / "nifty50.txt").read_text(encoding="utf-8").splitlines() if s.strip()]


def load_bars(symbols: list[str]) -> dict[str, pd.DataFrame]:
    raw = yf.download([s + ".NS" for s in symbols], period="60d", interval="5m", group_by="ticker",
                      progress=False, auto_adjust=False, threads=True)
    out = {}
    for s in symbols:
        try:
            df = raw[s + ".NS"].dropna(subset=["Open", "High", "Low", "Close"])
        except KeyError:
            continue
        if len(df):
            df = df.copy()
            df.index = df.index.tz_convert("Asia/Kolkata")
            out[s] = df
    return out


def replay(rets: np.ndarray, entry: float, stop: float, target: float, n_bars: int, runs: int, seed: int) -> dict:
    """Bootstrap the rest of the session from this stock's own 5-minute log returns."""
    if n_bars <= 0 or len(rets) < 50:
        return {"target_pct": None, "stop_pct": None, "neither_pct": None}
    rng = np.random.default_rng(seed)
    paths = entry * np.exp(np.cumsum(rng.choice(rets, size=(runs, n_bars), replace=True), axis=1))
    hit_t = paths >= target
    hit_s = paths <= stop
    first_t = np.where(hit_t.any(1), hit_t.argmax(1), n_bars + 1)
    first_s = np.where(hit_s.any(1), hit_s.argmax(1), n_bars + 1)
    t = np.mean(first_t < first_s) * 100
    s = np.mean(first_s < first_t) * 100
    return {"target_pct": round(float(t), 1), "stop_pct": round(float(s), 1), "neither_pct": round(100 - t - s, 1)}


def analyse(sym: str, df: pd.DataFrame, day, a) -> dict | None:
    today = df[df.index.date == day]
    if today.empty:
        return None
    rng_bars = today[(today.index.time >= OR_START) & (today.index.time < OR_END)]
    if len(rng_bars) < 4:
        return None
    or_high, or_low = float(rng_bars["High"].max()), float(rng_bars["Low"].min())
    h, m = (int(x) for x in a.last_entry.split(":"))
    after = today[(today.index.time >= OR_END) & (today.index.time <= time(h, m))]
    vol_ref = float(rng_bars["Volume"].mean()) or 1.0
    brk = after[(after["Close"] > or_high) & (after["Volume"] >= a.min_vol * vol_ref)]
    if brk.empty:
        return None
    bar_t = brk.index[0]
    entry = float(brk["Close"].iloc[0])
    stop = max(or_low, entry * (1 - a.max_stop_pct / 100))
    risk_ps = entry - stop
    if risk_ps <= 0:
        return None
    target = entry + a.rr * risk_ps
    budget = a.capital * a.risk_pct / 100
    qty = int(min(math.floor(budget / risk_ps), math.floor(a.capital / entry)))
    hist = df[df.index.date < day]
    hist = hist[(hist.index.time >= OR_START) & (hist.index.time < CLOSE_BY)]
    rets = np.diff(np.log(hist["Close"].to_numpy())) if len(hist) > 1 else np.array([])
    rets = rets[np.isfinite(rets)]
    n_bars = len(today[(today.index > bar_t) & (today.index.time < CLOSE_BY)]) if a.replay_rest_of_day else \
        int(((CLOSE_BY.hour * 60 + CLOSE_BY.minute) - (bar_t.hour * 60 + bar_t.minute)) / 5)
    rep = replay(rets, entry, stop, target, max(n_bars, 1), a.runs, a.seed)
    verdict = "SKIP" if rep["stop_pct"] is not None and rep["stop_pct"] >= a.skip_stop_pct else "CHECK"
    return {
        "symbol": sym, "breakout_time": bar_t.strftime("%H:%M"), "or_high": round(or_high, 2), "or_low": round(or_low, 2),
        "entry": round(entry, 2), "stop": round(stop, 2), "target": round(target, 2),
        "risk_per_share": round(risk_ps, 2), "shares": qty, "max_loss": round(qty * risk_ps, 2),
        "replays": a.runs, **rep, "verdict": verdict,
    }


def summary_ml(rows, day, a) -> str:
    if not rows:
        return f"{day}: Nifty 50-ൽ 9:45-ന് ശേഷം opening-range breakout ഒന്നും കണ്ടില്ല.\n\n{DISCLAIMER_ML}"
    out = [f"📅 {day} · Nifty 50 scan · capital ₹{a.capital:,.0f} · risk {a.risk_pct}%",
           f"⚡ {len(rows)} breakout(s) കണ്ടെത്തി.\n"]
    for r in rows:
        out.append(
            f"• {r['symbol']} ({r['breakout_time']}): entry ₹{r['entry']}, stop ₹{r['stop']}, target ₹{r['target']}. "
            f"{r['shares']} shares എടുത്താൽ stop-ൽ പരമാവധി നഷ്ടം ₹{r['max_loss']}. "
            f"{r['replays']:,} replays-ൽ target ആദ്യം: {r['target_pct']}%, stop ആദ്യം: {r['stop_pct']}%. "
            + ("➡️ പകുതിയോളം stop-ൽ പോകുന്നു, SKIP ചെയ്യാവുന്നതാണ്." if r["verdict"] == "SKIP" else "➡️ സ്വയം പരിശോധിച്ച് തീരുമാനിക്കുക."))
    out.append("\n" + DISCLAIMER_ML)
    return "\n".join(out)


def summary_en(rows, day, a) -> str:
    if not rows:
        return f"{day}: no Nifty 50 opening-range breakouts after 9:45.\n\n{DISCLAIMER}"
    out = [f"{day} · Nifty 50 scan · capital ₹{a.capital:,.0f} · risk {a.risk_pct}%", f"{len(rows)} breakout(s):\n"]
    for r in rows:
        out.append(f"- {r['symbol']} {r['breakout_time']}: entry {r['entry']}, stop {r['stop']}, target {r['target']}, "
                   f"{r['shares']} shares (max loss ₹{r['max_loss']}); {r['replays']:,} replays: target first "
                   f"{r['target_pct']}%, stop first {r['stop_pct']}% -> {r['verdict']}")
    out.append("\n" + DISCLAIMER)
    return "\n".join(out)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Claude Trading Assistant — Nifty 50 ORB helper (educational, not advice)")
    p.add_argument("--capital", type=float, default=100000)
    p.add_argument("--risk-pct", type=float, default=1.0)
    p.add_argument("--rr", type=float, default=2.0, help="target = entry + rr x (entry - stop)")
    p.add_argument("--max-stop-pct", type=float, default=2.0, help="stop is never further than this percent below entry")
    p.add_argument("--runs", type=int, default=10000)
    p.add_argument("--skip-stop-pct", type=float, default=50.0, help="flag SKIP when stop-first is at least this percent")
    p.add_argument("--date", help="YYYY-MM-DD (default: latest session in the data)")
    p.add_argument("--lang", choices=["ml", "en"], default="ml")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--top", type=int, default=5, help="show the best N (highest target-first share, SKIPs last)")
    p.add_argument("--last-entry", default="11:30", help="ignore breakouts after this time (HH:MM)")
    p.add_argument("--min-vol", type=float, default=1.5, help="breakout bar volume >= this x the opening-range average")
    p.add_argument("--replay-rest-of-day", action="store_true", help="replay only as many bars as the real session had")
    p.add_argument("--json", help="also write the rows to this JSON file")
    a = p.parse_args()

    syms = nifty50_symbols()
    bars = load_bars(syms)
    if not bars:
        sys.exit("No data from Yahoo Finance. Check your internet connection and try again.")
    days = sorted({d for df in bars.values() for d in df.index.date})
    day = pd.Timestamp(a.date).date() if a.date else days[-1]
    rows = [r for s, df in bars.items() if (r := analyse(s, df, day, a))]
    rows.sort(key=lambda r: (r["verdict"] != "CHECK", -(r["target_pct"] or 0)))
    total = len(rows)
    rows = rows[: a.top]
    print(f"Scanned {len(bars)}/{len(syms)} Nifty 50 stocks for {day}: {total} volume-confirmed breakout(s), showing top {len(rows)}.\n")
    if rows:
        print(pd.DataFrame(rows)[["symbol", "breakout_time", "entry", "stop", "target", "shares", "max_loss",
                                  "target_pct", "stop_pct", "verdict"]].to_string(index=False))
        print()
    print(summary_ml(rows, day, a) if a.lang == "ml" else summary_en(rows, day, a))
    if a.json:
        Path(a.json).write_text(json.dumps({"date": str(day), "rows": rows, "disclaimer": DISCLAIMER}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
