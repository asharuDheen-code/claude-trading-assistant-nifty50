# Claude Trading Assistant · Nifty 50 — Malayalam Setup Guide

**Orbynex** · WhatsApp 7012937250 · https://manageme.orbynex.io/

ശമ്പളം വേണ്ട, ലീവ് വേണ്ട 😄 Claude Code-ൽ **ഒറ്റ prompt** കൊടുത്താൽ Claude ഈ 4 ജോലി ചെയ്യും:

1. **Scan** — Nifty 50-ലെ 50 stocks-ഉം നോക്കി, 9:15–9:45 range-ന് മുകളിൽ volume-ഓടെ breakout ആയവ കണ്ടെത്തും.
2. **Plan** — ഓരോന്നിനും entry, stop (range-ന്റെ താഴെ, പരമാവധി 2%), target (risk-ന്റെ 2 ഇരട്ടി).
3. **Size** — stop-ൽ പോയാൽ നിങ്ങളുടെ capital-ന്റെ 1% (നിങ്ങൾ പറയുന്ന %) മാത്രം നഷ്ടം വരുന്ന രീതിയിൽ എത്ര share എടുക്കാം.
4. **Test** — ആ stock-ന്റെ കഴിഞ്ഞ ദിവസങ്ങളിലെ 5-minute നീക്കങ്ങൾ വെച്ച് ബാക്കി ദിവസം **10,000 തവണ replay** ചെയ്യും. Target ആദ്യം എത്ര %, stop ആദ്യം എത്ര %. പകുതിയോ അതിൽ കൂടുതലോ stop-ൽ പോയാൽ **SKIP**.

> ⚠️ **ഇത് financial advice അല്ല.** പഠിക്കാനും പരിശോധിക്കാനുമുള്ള tool മാത്രം. ഏത് stock വാങ്ങണം/വിൽക്കണം എന്ന് ഇത് പറയില്ല.
> Free data ഏകദേശം 15 മിനിറ്റ് വൈകിയാണ് വരിക. Replays പഴയ data-യുടെ model ആണ്, ഭാവി പ്രവചിക്കില്ല. Trading-ൽ നഷ്ടം വരാം.

## വേണ്ടത്
- **Claude Code** — Claude-ന്റെ paid plan (Pro) വേണം. Install: https://claude.com/claude-code
- **Python 3.10 അല്ലെങ്കിൽ പുതിയത്** — https://www.python.org/downloads/ (install ചെയ്യുമ്പോൾ "Add Python to PATH" tick ചെയ്യുക)
- Internet

## Setup (5 മിനിറ്റ്)
1. ഈ kit download ചെയ്യുക (GitHub-ൽ പച്ച **Code → Download ZIP**), unzip ചെയ്യുക.
2. ആ folder-ൽ terminal തുറന്ന് ഒരു തവണ മാത്രം:
   ```
   pip install -r requirements.txt
   ```
3. അതേ folder-ൽ Claude Code തുടങ്ങുക: `claude`
4. ഈ prompt paste ചെയ്യുക (capital-ഉം risk-ഉം നിങ്ങളുടേത് ആക്കുക):
   ```
   Nifty 50 scan ചെയ്ത് ഇന്നത്തെ opening-range breakouts കണ്ടെത്ത്. എന്റെ capital ₹1,00,000, risk 1%.
   ഓരോന്നിനും entry, stop, target, എത്ര share എന്ന് പറ. 10,000 replays run ചെയ്ത് result Malayalam-ൽ ചുരുക്കി പറഞ്ഞുതാ.
   ```
5. Result വായിക്കുക. ഓരോ breakout, share എണ്ണം, പരമാവധി നഷ്ടം, replay result എല്ലാം Claude Malayalam-ൽ പറഞ്ഞുതരും.

Market ഉള്ള ദിവസം **രാവിലെ 9:45-ന് ശേഷം** run ചെയ്യുക. പഴയ ഒരു ദിവസം നോക്കാൻ: `--date 2026-11-13`.

## "CHECK" എന്നാൽ?
SKIP flag ഇല്ല എന്ന് മാത്രം. **വാങ്ങാനുള്ള signal അല്ല.** തീരുമാനം നിങ്ങളുടേതാണ്.

## സഹായം വേണോ? Custom version വേണോ?
WhatsApp **7012937250** · Instagram **@orbynex.io**
