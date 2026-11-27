"""Backtest the kit's Nifty 50 opening-range-breakout rules on real 5-minute data, WITH trading charges.

For every past session (Yahoo gives ~60 days of 5-minute bars) and every Nifty 50 stock with a breakout,
it walks the real bars after entry: stop first (or same bar) = -1R, target first = +rr R,
neither by 15:20 = exit at that bar's close. Then it subtracts approximate Indian intraday equity charges.

Educational / research only. Not investment advice. Past results do not predict future results.

    python backtest.py                         # ₹1 lakh, 1% risk, defaults
    python backtest.py --capital 200000 --risk-pct 0.5 --rr 1.5 --lang en
    python backtest.py --brokerage 0           # e.g. a zero-brokerage plan (STT/GST etc. still apply)
"""
import argparse
import json
import sys
from types import SimpleNamespace

import assistant as k


def charges(entry: float, exit_px: float, qty: int, brokerage_cap: float) -> float:
    """Approximate intraday equity charges (NSE). Check your broker's calculator; rates change."""
    buy, sell = qty * entry, qty * exit_px
    br = min(brokerage_cap, 0.0003 * buy) + min(brokerage_cap, 0.0003 * sell)  # per order: flat cap or 0.03%
    txn = 0.0000297 * (buy + sell)          # NSE transaction charge
    sebi = (buy + sell) * 1e-7              # SEBI fee ₹10 / crore
    stt = 0.00025 * sell                    # STT 0.025% on the sell side
    stamp = 0.00003 * buy                   # stamp duty 0.003% on the buy side
    gst = 0.18 * (br + txn + sebi)
    return br + txn + sebi + stt + stamp + gst


def main():
    p = argparse.ArgumentParser(description="ORB backtest with charges (educational, not advice)")
    p.add_argument("--capital", type=float, default=100000)
    p.add_argument("--risk-pct", type=float, default=1.0)
    p.add_argument("--rr", type=float, default=2.0)
    p.add_argument("--max-stop-pct", type=float, default=2.0)
    p.add_argument("--min-vol", type=float, default=1.5)
    p.add_argument("--last-entry", default="11:30")
    p.add_argument("--brokerage", type=float, default=20.0, help="max brokerage per order in ₹ (0 for zero-brokerage plans)")
    p.add_argument("--skip-filter", action="store_true", help="also run the kit's 10,000-replay SKIP filter (slower)")
    p.add_argument("--lang", choices=["ml", "en"], default="ml")
    p.add_argument("--json", help="write every trade to this JSON file")
    a = p.parse_args()
    cfg = SimpleNamespace(capital=a.capital, risk_pct=a.risk_pct, rr=a.rr, max_stop_pct=a.max_stop_pct,
                          runs=10000 if a.skip_filter else 50, skip_stop_pct=50.0, seed=7,
                          last_entry=a.last_entry, min_vol=a.min_vol, replay_rest_of_day=False)

    bars = k.load_bars(k.nifty50_symbols())
    days = sorted({d for df in bars.values() for d in df.index.date})
    trades = []
    for day in days[5:-1]:  # skip the first days (replay history) and today (session not finished)
        for sym, df in bars.items():
            r = k.analyse(sym, df, day, cfg)
            if not r or r["shares"] <= 0:
                continue
            today = df[df.index.date == day]
            h, m = (int(x) for x in r["breakout_time"].split(":"))
            after = today[[(t.hour, t.minute) > (h, m) and t.time() < k.CLOSE_BY for t in today.index]]
            risk = r["entry"] - r["stop"]
            res, exit_px = "neither", float(after["Close"].iloc[-1]) if len(after) else r["entry"]
            for _, b in after.iterrows():
                if b["Low"] <= r["stop"]:
                    res, exit_px = "stop", r["stop"]
                    break
                if b["High"] >= r["target"]:
                    res, exit_px = "target", r["target"]
                    break
            gross = (exit_px - r["entry"]) * r["shares"]
            cost = charges(r["entry"], exit_px, r["shares"], a.brokerage)
            trades.append({"day": str(day), **r, "result": res, "exit": round(exit_px, 2),
                           "gross": round(gross, 2), "charges": round(cost, 2), "net": round(gross - cost, 2),
                           "R": round((exit_px - r["entry"]) / risk, 3)})

    if not trades:
        sys.exit("No breakout trades found in the data.")
    n = len(trades)
    pct = lambda x: round(100 * sum(t["result"] == x for t in trades) / n, 1)  # noqa: E731
    gross = sum(t["gross"] for t in trades)
    cost = sum(t["charges"] for t in trades)
    d0, d1 = trades[0]["day"], trades[-1]["day"]
    days_n = len({t["day"] for t in trades})
    if a.lang == "ml":
        print(f"Backtest: Nifty 50 ORB · {days_n} ദിവസം ({d0} → {d1}) · {n} trades")
        print(f"Target ആദ്യം: {pct('target')}% · Stop ആദ്യം: {pct('stop')}% · രണ്ടുമില്ല: {pct('neither')}%")
        print(f"Charges ഇല്ലാതെ: ₹{gross:,.0f} · Charges: ₹{cost:,.0f} (ഒരു trade-ന് ~₹{cost / n:,.0f})")
        print(f"Charges കൂട്ടിയ ശേഷം: ₹{gross - cost:,.0f}")
        print("⚠️ പഠിക്കാൻ മാത്രം. Financial advice അല്ല. പഴയ റിസൾട്ട് ഭാവി പ്രവചിക്കില്ല.")
    else:
        print(f"Backtest: Nifty 50 ORB · {days_n} days ({d0} → {d1}) · {n} trades")
        print(f"Target first: {pct('target')}% · Stop first: {pct('stop')}% · Neither: {pct('neither')}%")
        print(f"Before charges: ₹{gross:,.0f} · Charges: ₹{cost:,.0f} (~₹{cost / n:,.0f} per trade)")
        print(f"After charges: ₹{gross - cost:,.0f}")
        print("⚠️ Educational only. Not investment advice. Past results don't predict future results.")
    if a.json:
        json.dump(trades, open(a.json, "w", encoding="utf-8"), indent=1, default=str)


if __name__ == "__main__":
    main()
