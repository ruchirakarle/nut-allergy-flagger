import pandas as pd
import re

from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

NUT_TAGS = {"en:nuts"}  # add "en:peanuts" here to count peanuts as nuts too

# ---------- Step 3: Cleaning ----------
df = pd.read_csv("data/products.csv", dtype={"code": str})
print(f"loaded: {len(df)}")

for col in [
    "ingredients_text_en",
    "ingredients_text",
    "lang",
    "allergens_tags",
    "traces_tags",
]:
    df[col] = df[col].fillna("")

# English text: use ingredients_text_en; if empty, fall back to
# ingredients_text only when the product's main language is English
df["text"] = df["ingredients_text_en"].str.strip()
fallback = (df["text"] == "") & (df["lang"] == "en")
df.loc[fallback, "text"] = df.loc[fallback, "ingredients_text"].str.strip()

print(
    f"no ingredients at all: {((df['ingredients_text_en'] == '') & (df['ingredients_text'] == '')).sum()}"
)
df = df[df["text"] != ""].copy()
print(f"kept (English ingredients): {len(df)}")


def has_nut_tag(tags):
    return int(any(t in NUT_TAGS for t in tags.split(",")))


df["label"] = df["allergens_tags"].apply(has_nut_tag)

print("\nclass balance:")
print(df["label"].value_counts())
print(df["label"].value_counts(normalize=True).round(3))

traces_only = (df["label"] == 0) & df["traces_tags"].apply(has_nut_tag).astype(bool)
print(f"\nnuts in traces only (labeled 0): {traces_only.sum()}")

# ---------- Train/test split (shared by both models) ----------
train_df, test_df = train_test_split(
    df, test_size=0.25, stratify=df["label"], random_state=42
)
print(f"\ntrain: {len(train_df)}  test: {len(test_df)}  "
      f"test positives: {test_df['label'].sum()}")


# ---------- Scoring helper (Step 6) ----------
def score(name, y_true, y_pred):
    p = precision_score(y_true, y_pred, zero_division=0)
    r = recall_score(y_true, y_pred, zero_division=0)
    f = f1_score(y_true, y_pred, zero_division=0)
    print(f"\n=== {name} ===")
    print(f"precision {p:.3f}   recall {r:.3f}   F1 {f:.3f}")
    print("confusion matrix  [[TN FP]\n                   [FN TP]]")
    print(confusion_matrix(y_true, y_pred))


# ---------- Step 4: Keyword baseline ----------
KEYWORDS = ["nut", "almond", "hazelnut", "cashew", "walnut", "pecan", "pistachio"]


def keyword_predict(text):
    text = text.lower()
    return int(any(k in text for k in KEYWORDS))


test_df = test_df.copy()
test_df["kw_pred"] = test_df["text"].apply(keyword_predict)
score("Keyword rule", test_df["label"], test_df["kw_pred"])

# ---------- Step 5: TF-IDF + logistic regression ----------
model = make_pipeline(
    TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=2),
    LogisticRegression(max_iter=1000, class_weight="balanced"),
)
model.fit(train_df["text"], train_df["label"])
test_df["lr_pred"] = model.predict(test_df["text"])
score("TF-IDF + LogReg", test_df["label"], test_df["lr_pred"])

# Which terms push hardest toward "contains nuts"?
words = model.named_steps["tfidfvectorizer"].get_feature_names_out()
weights = model.named_steps["logisticregression"].coef_[0]
top = weights.argsort()[-15:][::-1]
print("\ntop nut-predicting terms:", [words[i] for i in top])

# ---------- Step 7: Error analysis ----------
def show_errors(pred_col, kind, n=15):
    if kind == "FP":
        rows = test_df[(test_df[pred_col] == 1) & (test_df["label"] == 0)]
    else:
        rows = test_df[(test_df[pred_col] == 0) & (test_df["label"] == 1)]
    print(f"\n##### {pred_col} {kind}: showing {min(n, len(rows))} of {len(rows)} #####")
    for _, r in rows.head(n).iterrows():
        matched = [k for k in KEYWORDS if k in r["text"].lower()]
        print(f"\n- {r['product_name']}")
        print(f"  allergens: {r['allergens_tags'] or '(none)'}  |  traces: {r['traces_tags'] or '(none)'}")
        print(f"  keywords found: {matched or '(none)'}")
        print(f"  text: {r['text']}")


show_errors("kw_pred", "FP")
show_errors("kw_pred", "FN")
show_errors("lr_pred", "FP")
show_errors("lr_pred", "FN")

# ---------- Step 8: Fix - whole-word keyword matching ----------
PATTERN = re.compile(r"\b(" + "|".join(KEYWORDS) + r")s?\b")


def keyword_predict_v2(text):
    return int(bool(PATTERN.search(text.lower())))


test_df["kw_pred_v2"] = test_df["text"].apply(keyword_predict_v2)
score("Keyword rule BEFORE (substring)", test_df["label"], test_df["kw_pred"])
score("Keyword rule AFTER (whole word)", test_df["label"], test_df["kw_pred_v2"])

show_errors("kw_pred_v2", "FP")
show_errors("kw_pred_v2", "FN")