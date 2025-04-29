import requests
from bs4 import BeautifulSoup
import os
import re
import time

def sanitize_filename(filename):
    """Remove characters that are not safe for filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

def normalize_title(title):
    """Normalize book titles for deduplication: lowercase, remove all non-alphanumeric characters."""
    return re.sub(r'[^0-9a-z]+', '', title.lower())

def looks_like_prose(text, letter_ratio_thresh=0.7, common_words=None):
    """
    Return True if `text` looks like English prose:
      - at least `letter_ratio_thresh` fraction of characters are A–Z/a–z or space
      - contains at least 2 of the common English words
    """
    if common_words is None:
        common_words = [" the ", " and ", " to ", " of ", " in "]
    snippet = text[:10000]  # only inspect first 10k chars
    if len(snippet) < 500:   # too short to be a real book
        return False

    # Letter/space ratio
    letter_count = sum(1 for c in snippet if c.isalpha() or c.isspace())
    if letter_count / len(snippet) < letter_ratio_thresh:
        return False

    # Common word check
    low = snippet.lower()
    hits = sum(1 for w in common_words if w in low)
    return hits >= 2

download_dir = "Gutenberg_Books"
os.makedirs(download_dir, exist_ok=True)

seen_titles = set()
downloaded_count = 0

# Preload any already-downloaded titles
for fname in os.listdir(download_dir):
    if fname.lower().endswith('.txt'):
        seen_titles.add(normalize_title(os.path.splitext(fname)[0]))

book_id = 1
while downloaded_count < 130:
    details_url = f"https://www.gutenberg.org/ebooks/{book_id}"
    try:
        resp = requests.get(details_url, timeout=10)
    except requests.RequestException:
        book_id += 1
        continue

    if resp.status_code != 200:
        book_id += 1
        continue

    soup = BeautifulSoup(resp.text, "html.parser")

    title_el = soup.find("h1", {"itemprop": "name"})
    if not title_el:
        book_id += 1
        continue
    title = title_el.get_text(strip=True)
    key = normalize_title(title)
    if key in seen_titles:
        book_id += 1
        continue

    lang_el = soup.find("th", string="Language")
    language = lang_el.find_next_sibling("td").get_text(strip=True) if lang_el else ''
    if "English" not in language:
        book_id += 1
        continue

    # Find a .txt link
    txt_link = None
    for link in soup.select("a[type='text/plain'], a[href$='.txt']"):
        href = link.get("href", "")
        if href.endswith(".txt"):
            txt_link = href if href.startswith("http") else f"https://www.gutenberg.org{href}"
            break
    if not txt_link:
        txt_link = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"

    try:
        r = requests.get(txt_link, timeout=10)
    except requests.RequestException:
        book_id += 1
        continue

    if r.status_code == 200:
        # decode and filter
        text = r.content.decode('utf-8', errors='ignore')
        if looks_like_prose(text):
            safe_title = sanitize_filename(title)[:200]
            path = os.path.join(download_dir, f"{safe_title}.txt")
            with open(path, "wb") as f:
                f.write(r.content)
            seen_titles.add(key)
            downloaded_count += 1
            print(f"[{downloaded_count}] Saved: {title}")
        else:
            print(f"Skipped (not prose): {title}")

    book_id += 1
    time.sleep(0.5)  # be polite

print(f"Done: downloaded {downloaded_count} English prose books into '{download_dir}'")
