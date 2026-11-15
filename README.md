# Claude Trading Assistant · Nifty 50 (free setup kit)

**by [Orbynex](https://manageme.orbynex.io/)** · Malayalam guide: [GUIDE_ML.md](GUIDE_ML.md)

No salary, no leave 😄 Claude does four jobs for you from **one prompt** in Claude Code:

| Job | What it does |
|---|---|
| 1. **Scan** | Checks all Nifty 50 stocks for a volume-confirmed breakout above the 9:15–9:45 opening range |
| 2. **Plan** | Entry, stop (other side of the range, max 2% away) and target (2× the risk) |
| 3. **Size** | How many shares, so that hitting the stop loses only your chosen risk % of capital |
| 4. **Test** | Replays the rest of the day 10,000 times from the stock's own recent 5-minute moves: how often the target came first vs the stop. If half or more hit the stop → **SKIP** |

> ⚠️ **Not financial advice.** An educational / research tool. It does not tell you to buy or sell anything.
> Free data is delayed ~15 minutes. Replays model the past and do not predict the future. Trading involves risk of loss.

## You need
- **Claude Code** — needs a paid Claude plan (Pro or above). Install: https://claude.com/claude-code
- **Python 3.10+** — https://www.python.org/downloads/
- Internet (data comes free from NSE's index list + Yahoo Finance)

## Setup (5 minutes)
1. Download this kit (green **Code → Download ZIP**) and unzip it, or `git clone` it.
2. Open a terminal in the folder and run once:
   ```
   pip install -r requirements.txt
   ```
3. Start Claude Code in the same folder: `claude`
4. Paste the prompt from [PROMPT.md](PROMPT.md) (change capital and risk to yours).
5. Read the result. Claude explains each breakout, the share count, the maximum loss and the replay result.

Run it after **9:45 AM IST** on a market day (or pass `--date YYYY-MM-DD` for a past session).

## Without Claude (plain Python)
```
python assistant.py --capital 100000 --risk-pct 1 --lang ml
python assistant.py --capital 100000 --risk-pct 1 --lang en --date 2026-11-13
```
Options: `--rr 2` reward:risk · `--max-stop-pct 2` · `--min-vol 1.5` breakout volume vs opening range ·
`--last-entry 11:30` · `--top 5` · `--runs 10000` · `--skip-stop-pct 50` · `--json out.json`

## Example (13 Nov 2026, ₹1,00,000 capital, 1% risk) — illustration only
```
    symbol breakout_time  entry    stop  target  shares  max_loss  target_pct  stop_pct verdict
TATACONSUM         10:10 1084.3 1076.10  1100.7      92    754.41        19.1      46.3   CHECK
 SUNPHARMA         09:55 1905.9 1891.30  1935.1      52    759.20        16.7      45.7   CHECK
```
"CHECK" only means "not flagged SKIP" — it is **not** a buy signal.

## Need help or a custom version?
WhatsApp **7012937250** · https://manageme.orbynex.io/ · Instagram [@orbynex.io](https://instagram.com/orbynex.io)

MIT licence. Use at your own risk.
