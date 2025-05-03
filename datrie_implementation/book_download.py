#!/usr/bin/env python3
import os
import re
import time
import requests

# ——— Configuration ———
DOWNLOAD_DIR = "Gutenberg_Books"
TARGET_COUNT = 130
TOPICS = [
    "Fiction",
    "Historical Fiction",
    "Children’s Fiction",
    "Mystery & Detective Stories",
    "Science Fiction",
    "Fantasy",
    "Romance",
    "Essays",
]
API_URL = "https://gutendex.com/books"
SLEEP_BETWEEN_DOWNLOADS = 0.2  # seconds

# ——— Helpers ———
def sanitize_filename(filename):
    """Remove characters unsafe for filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

def normalize_title(title):
    """Normalize for deduplication: lowercase, alphanumeric only."""
    return re.sub(r'[^0-9a-z]+', '', title.lower())

def looks_like_prose(text, letter_ratio_thresh=0.7, min_length=500):
    """
    Heuristic check for English prose:
      1) text length ≥ min_length
      2) ≥ letter_ratio_thresh fraction of chars are letters/spaces
      3) contains ≥2 of the common English words
    """
    snippet = text[:10000]
    if len(snippet) < min_length:
        return False
    letter_count = sum(1 for c in snippet if c.isalpha() or c.isspace())
    if letter_count / len(snippet) < letter_ratio_thresh:
        return False
    low = snippet.lower()
    common_words = [" the ", " and ", " to ", " of ", " in "]
    hits = sum(1 for w in common_words if w in low)
    return hits >= 2

# ——— Prepare download folder & state ———
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
seen = set()  # normalized main titles + authors
count = 0

# ——— Main loop: iterate topics and pages ———
for topic in TOPICS:
    page = 1
    while count < TARGET_COUNT:
        params = {
            "languages": "en",
            "topic": topic,
            "page": page
        }
        try:
            resp = requests.get(API_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException:
            break  # skip this topic if API call fails

        results = data.get("results", [])
        if not results:
            break

        for book in results:
            if count >= TARGET_COUNT:
                break

            # 1) Extract and truncate at first ':' or ';'
            raw_title = book.get("title", "untitled")
            main_title = re.split(r'[:;]', raw_title)[0].strip()

            # 2) Get author (first one if multiple)
            authors = book.get("authors", [])
            if authors:
                author_name = authors[0].get("name", "").strip()
            else:
                author_name = "Unknown"

            # 3) Combine for filename and dedupe key
            combined = f"{main_title} - {author_name}"
            key = normalize_title(combined)
            if key in seen:
                continue

            # 4) Pick best plain‐text URL
            fmts = book.get("formats", {})
            txt_url = (
                fmts.get("text/plain; charset=utf-8")
                or fmts.get("text/plain")
                or next((u for k, u in fmts.items() if k.startswith("text/plain")), None)
            )
            if not txt_url:
                continue

            # 5) Download the text
            try:
                r = requests.get(txt_url, timeout=10)
                r.raise_for_status()
            except requests.RequestException:
                continue

            text = r.content.decode("utf-8", errors="ignore")
            if not looks_like_prose(text):
                continue

            # 6) Save file
            safe_name = sanitize_filename(combined)[:200] or f"book_{book['id']}"
            path = os.path.join(DOWNLOAD_DIR, f"{safe_name}.txt")
            with open(path, "wb") as f:
                f.write(r.content)

            seen.add(key)
            count += 1
            print(f"[{count}] Saved: {combined}")

            time.sleep(SLEEP_BETWEEN_DOWNLOADS)

        # move to next page if available
        if not data.get("next"):
            break
        page += 1

    if count >= TARGET_COUNT:
        break

print(f"Done: downloaded {count} English novels/essays into “{DOWNLOAD_DIR}”")
