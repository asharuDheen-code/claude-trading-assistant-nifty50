# Strategy Backtest (charges ഉൾപ്പെടെ) · മലയാളം Guide

**Orbynex** · https://manageme.orbynex.io/

ഒരു strategy-യിൽ പൈസ ഇറക്കുന്നതിന് മുമ്പ്, കഴിഞ്ഞ ~2 മാസത്തെ ശരിക്കുള്ള 5-minute data-യിൽ അത് എങ്ങനെ പോയേനെ എന്ന് Claude-നെക്കൊണ്ട് test ചെയ്യിക്കാം. **Brokerage, STT, GST എല്ലാം കൂട്ടിയിട്ട്.**

> ⚠️ **ഇത് financial advice അല്ല.** പഠിക്കാനുള്ള tool മാത്രം. ഏത് stock വാങ്ങണം/വിൽക്കണം എന്ന് പറയില്ല. പഴയ റിസൾട്ട് ഭാവി പ്രവചിക്കില്ല. Charges ഏകദേശ കണക്കാണ്; നിങ്ങളുടെ broker-ന്റെ calculator-ൽ നോക്കുക.

## Setup
ഈ kit-ന്റെ [README](README.md)-ലെ setup ചെയ്താൽ മതി (Claude Code + Python + `pip install -r requirements.txt`).

## Claude Code-ൽ ഈ prompt ഇടുക
```
backtest.py വെച്ച് Nifty 50 ORB strategy backtest ചെയ്യ്. എന്റെ capital ₹1,00,000, risk 1%.
Charges കൂട്ടുന്നതിന് മുമ്പും ശേഷവുമുള്ള result Malayalam-ൽ ചുരുക്കി പറ. എന്തുകൊണ്ട് ഇങ്ങനെ വന്നു എന്നും.
```

## Claude ഇല്ലാതെ (plain Python)
```
python backtest.py
python backtest.py --capital 200000 --risk-pct 0.5 --rr 1.5
python backtest.py --brokerage 0      # zero-brokerage plan ആണെങ്കിൽ
```

## Result എങ്ങനെ വായിക്കാം
- **Target ആദ്യം / Stop ആദ്യം / രണ്ടുമില്ല:** ഓരോ trade-ലും ശരിക്കുള്ള chart-ൽ ആദ്യം എന്ത് സംഭവിച്ചു.
- **Charges ഇല്ലാതെ vs Charges കൂട്ടിയ ശേഷം:** ഒരുപാട് trade എടുക്കുന്ന strategy-കളിൽ charges ലാഭം മുഴുവൻ തിന്നുതീർക്കും.
- Rules മാറ്റി (rr, risk, last entry time) വീണ്ടും test ചെയ്ത് നോക്കുക. ഒരു setting മാത്രം നോക്കി തീരുമാനിക്കരുത്.

## ഞങ്ങളുടെ reel-ലെ result (7 Sep – 26 Nov 2026)
780 trades · Target ആദ്യം 4.2% · Charges ഇല്ലാതെ +₹9,978 · Charges കൂട്ടിയപ്പോൾ −₹46,263 (₹1 lakh, 1% risk).
