# 🥜 Nut Flagger

Paste a food's ingredient list and find out if it contains tree nuts or peanuts.

**Live demo:** https://nut-allergy-flagger.vercel.app/

> ⚠️ **Demo only.** This is a simple keyword matcher, not a safety tool. It can miss nuts.
> Always read the real product label, and ask a doctor if you have a serious allergy.

## What it does

- 🚫 **Contains nuts**: lists the tree nuts and peanuts it found.
- ⚠️ **May contain traces**: the label only has a "may contain" or "processed in a facility" warning.
- ✅ **No nuts spotted**: no nut words found.

It handles tricky cases: coconut, nutmeg and butternut squash are not flagged, "nut-free" is ignored, and pine nuts get a note that they are technically seeds.

## How it was built

1. `fetch_data.py` downloads about 800 products from [Open Food Facts](https://world.openfoodfacts.org/), including their ingredient text and allergen tags.
2. `flagger.py` compares a substring keyword rule, a whole-word keyword rule, and a TF-IDF + logistic regression model, and prints the errors for each.
3. Whole-word keywords won, so they became the checker in `nutlogic.py`.
4. `evaluate_nutlogic.py` scores it against the Open Food Facts allergen labels.

| Model | Precision | Recall | F1 |
|---|---|---|---|
| Keyword rule (substring) | 0.519 | 1.000 | 0.684 |
| TF-IDF + logistic regression | 0.656 | 0.778 | 0.712 |
| Keyword rule (whole word) | 0.758 | 0.926 | 0.833 |
| Final checker (`nutlogic.py`, includes peanuts and trace warnings) | 0.933 | 0.975 | 0.953 |

The last row counts "may contain" as flagged, so it isn't a direct comparison with the rows above it. Some "errors" are label mistakes in the data, such as products with pecans or almond butter that aren't tagged as nuts.

## Project layout

| File | Purpose |
|---|---|
| `web/index.html` | Static site deployed on Vercel (checker rewritten in JavaScript) |
| `vercel.json` | Tells Vercel to serve the `web/` folder |
| `app.py` | Same interface as a Streamlit app |
| `nutlogic.py` | The Python checker |
| `evaluate_nutlogic.py` | Scores the checker on the dataset |
| `fetch_data.py`, `flagger.py` | Data download and model comparison |

The word list lives in both `nutlogic.py` and `web/index.html`. If you add a nut word, add it in both.

## Run it yourself

```bash
python -m venv .venv
.venv/Scripts/activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt

python fetch_data.py          # download the dataset (once)
python flagger.py             # compare models
python evaluate_nutlogic.py   # score the final checker
streamlit run app.py          # Streamlit interface
```

For the static site, open `web/index.html` in a browser.

## Known limits

- Keyword matching only. It misses misspellings, other languages, and hidden terms like "natural flavor".
- It caught about 97% of nut products in testing, so some were missed.
- Labels in Open Food Facts are crowd-sourced and sometimes wrong.

Data: [Open Food Facts](https://world.openfoodfacts.org/), available under the Open Database License.
