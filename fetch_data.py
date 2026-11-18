import time
from pathlib import Path

import pandas as pd
import requests

URL = "https://world.openfoodfacts.org/api/v2/search"
HEADERS = {"User-Agent": "NutFlagger/0.1 (your-email@example.com)"}  # put your email
FIELDS = "code,product_name,ingredients_text_en,ingredients_text,lang,allergens_tags,traces_tags"
PAGE_SIZE = 100
N_PAGES = 10
PAUSE_SECONDS = 7  # stays under 10 search requests/minute
OUT = Path("data/products.csv")


def fetch_page(page):
    params = {
        "fields": FIELDS,
        "page_size": PAGE_SIZE,
        "page": page,
        "countries_tags": "en:united-states",  # biases toward English labels
    }
    for attempt in range(3):
        try:
            r = requests.get(URL, params=params, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return r.json().get("products", [])
            print(f"page {page}: HTTP {r.status_code}, retrying")
        except requests.RequestException as e:
            print(f"page {page}: {e}, retrying")
        time.sleep(15 * (attempt + 1))  # back off longer each retry
    return []


def main():
    if OUT.exists():
        print(f"{OUT} exists, skipping fetch (delete it to refetch)")
        return
    rows = []
    for page in range(1, N_PAGES + 1):
        products = fetch_page(page)
        print(f"page {page}: {len(products)} products")
        rows.extend(products)
        time.sleep(PAUSE_SECONDS)

    df = pd.DataFrame(rows).drop_duplicates("code")
    for col in ["allergens_tags", "traces_tags"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: ",".join(x) if isinstance(x, list) else ""
            )
    df.to_csv(OUT, index=False)
    print(f"saved {len(df)} products to {OUT}")


if __name__ == "__main__":
    main()
