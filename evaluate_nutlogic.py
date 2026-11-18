"""Score nutlogic.check against the Open Food Facts labels."""
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from nutlogic import check

df = pd.read_csv("data/products.csv", dtype={"code": str}).fillna("")
df["text"] = df["ingredients_text_en"].str.strip()
fb = (df["text"] == "") & (df["lang"] == "en")
df.loc[fb, "text"] = df.loc[fb, "ingredients_text"].str.strip()
df = df[df["text"] != ""]

has = lambda tags: int(any(t in ("en:nuts", "en:peanuts") for t in tags.split(",")))
df["label"] = df["allergens_tags"].apply(has)
df["pred"] = df["text"].apply(lambda t: int(check(t).status != "clear"))
y, p = df["label"], df["pred"]
print(f"n={len(df)}  precision {precision_score(y, p):.3f}  recall {recall_score(y, p):.3f}  F1 {f1_score(y, p):.3f}")
print(confusion_matrix(y, p))
