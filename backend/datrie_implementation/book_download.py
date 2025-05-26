import os
import re
import time
import requests

# Configuration 
DOWNLOAD_DIR = "Gutenberg_Books"       # Folder to save downloaded books
TARGET_COUNT = 130                     # Total number of books to download
BOOKSHELVES = [                        # Bookshelf categories to pull from
    "Science Fiction",
    "Historical Fiction",
    "Children",
    "Mystery",
    "Fantasy",
    "Romance",
    "Essays",
    "Adventure",
]
API_URL = "https://gutendex.com/books" # Gutendex API endpoint
SLEEP_BETWEEN_DOWNLOADS = 0.2          # Delay between downloads (seconds)

# Helpers 
def sanitize_filename(filename):
    """Remove characters unsafe for filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

def normalize_title(title):
    """Normalize for deduplication: lowercase, alphanumeric only."""
    return re.sub(r'[^0-9a-z]+', '', title.lower())

def looks_like_prose(text, letter_ratio_thresh=0.7, min_length=500):
    """
    Heuristic check for English prose:
      - Length ≥ min_length
      - ≥ letter_ratio_thresh of chars are letters/spaces
      - Contains ≥2 common English words
    """
    snippet = text[:10000]  # limit scope to the first 10k characters
    if len(snippet) < min_length:
        return False
    letter_count = sum(1 for c in snippet if c.isalpha() or c.isspace())
    if letter_count / len(snippet) < letter_ratio_thresh:
        return False
    low = snippet.lower()
    common_words = [" the ", " and ", " to ", " of ", " in "]  # common indicators
    hits = sum(1 for w in common_words if w in low)
    return hits >= 2

# Prepare download folder & state 
os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # create folder if it doesn’t exist
seen = set()   # track already downloaded books 
count = 0      # current download count

# Main loop: iterate bookshelves and pages 
for shelf in BOOKSHELVES:
    page = 1  # start from the first page
    while count < TARGET_COUNT:
        params = {
            "languages": "en",        # restrict to English books
            "bookshelves": shelf,     # current bookshelf category
            "page": page              # page of results
        }
        try:
            resp = requests.get(API_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()        # parse response JSON
        except requests.RequestException:
            break  # skip this shelf if API fails

        results = data.get("results", [])
        if not results:
            break  # no books returned, go to next shelf

        for book in results:
            if count >= TARGET_COUNT:
                break  # stop if target reached

            raw_title = book.get("title", "untitled")
            main_title = re.split(r'[:;]', raw_title)[0].strip()  # remove subtitles
            authors = book.get("authors", [])
            author_name = authors[0].get("name", "").strip() if authors else "Unknown"
            combined = f"{main_title} - {author_name}"  # used for filename and deduping
            key = normalize_title(combined)
            if key in seen:
                continue  # skip duplicates

            fmts = book.get("formats", {})
            # Prefer UTF-8 plain text, fallback to any plain text if needed
            txt_url = (
                fmts.get("text/plain; charset=utf-8")
                or fmts.get("text/plain")
                or next((u for k, u in fmts.items() if k.startswith("text/plain")), None)
            )
            if not txt_url:
                continue  # skip if no plain text format available

            try:
                r = requests.get(txt_url, timeout=10)
                r.raise_for_status()
            except requests.RequestException:
                continue  # skip if download fails

            text = r.content.decode("utf-8", errors="ignore")  # decode with fallback
            if not looks_like_prose(text):
                continue  # skip if it doesn’t look like valid prose

            # Sanitize and truncate filename if needed
            safe_name = sanitize_filename(combined)[:200] or f"book_{book['id']}"
            path = os.path.join(DOWNLOAD_DIR, f"{safe_name}.txt")
            with open(path, "wb") as f:
                f.write(r.content)  # save book to file

            seen.add(key)  # mark book as downloaded
            count += 1
            print(f"[{count}] Saved: {combined}")  # log saved book

            time.sleep(SLEEP_BETWEEN_DOWNLOADS)  # brief pause between downloads

        if not data.get("next"):
            break  # no more pages in this shelf
        page += 1  # go to next page

    if count >= TARGET_COUNT:
        break  # overall limit reached

print(f"Done: downloaded {count} English novels/essays into “{DOWNLOAD_DIR}”")
