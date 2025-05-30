import requests
from bs4 import BeautifulSoup
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def sanitize_filename(filename):
    """
    Removes characters that are not allowed in filenames
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

def clean_text(text):
    """
    Converts text to lowercase, removes non-alphabetic characters, and collapses whitespace
    """
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    return re.sub(r'\s+', ' ', text).strip()

# URL for Project Gutenberg's top 100 books
url = "https://www.gutenberg.org/browse/scores/top"
download_dir = "Gutenberg_Top_100"

# Ensures download directory exists
os.makedirs(download_dir, exist_ok=True)

def fetch_book_links():
    """
    Scrapes the top 100 book links from the Project Gutenberg page
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select("ol a[href^='/ebooks/']")

def download_book(book_id, book_title, existing_files):
    """
    Downloads and cleans a book by its ID
    Returns the lowercase sanitized title if successful
    Skips books that are not in English or already downloaded
    """
    safe_title = sanitize_filename(book_title)
    lower_title = safe_title.lower()

    if lower_title in existing_files:
        print(f"Skipping {book_title} — book already exists.")
        return False

    file_path = os.path.join(download_dir, f"{safe_title}.txt")

    try:
        # Construct raw text URL
        book_text_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
        r = requests.get(book_text_url, timeout=10)

        if r.status_code == 200:
            clean_content = clean_text(r.text)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(clean_content)
            print(f"Downloaded and cleaned: {book_title}")
            return lower_title
        else:
            print(f"Found .txt link but request failed ({r.status_code}) for {book_title}")
        return False
    
    except Exception as e:
        print(f"Error downloading {book_title}: {e}")
        return False

def main():
    """
    Downloads up to 100 top books from Project Gutenberg,
    skipping already-downloaded books and filtering only English texts.
    Uses multithreading to download books in parallel.
    """
    # Detect already downloaded files
    existing_files = {sanitize_filename(f).lower() for f in os.listdir(download_dir) if f.endswith(".txt")}
    total_needed = 100 - len(existing_files)

    if total_needed <= 0:
        print("There are already 100 books")
        return

    print(f"Need {total_needed} more books. Starting download...")

    book_links = fetch_book_links()
    downloaded_count = 0
    index = 0
    used_titles = set(existing_files)

    # Multithreaded download using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:
        while downloaded_count < total_needed and index < len(book_links):
            futures = []

            # Schedule up to 10 books at a time
            while len(futures) < 10 and index < len(book_links):
                link = book_links[index]
                book_id = link["href"].split("/")[-1]
                book_title = link.get_text(strip=True)
                futures.append(executor.submit(download_book, book_id, book_title, used_titles))
                index += 1

            # Wait for all downloads in this batch
            for future in as_completed(futures):
                result = future.result()
                if result and result not in used_titles:
                    used_titles.add(result)
                    downloaded_count += 1
                    if downloaded_count >= total_needed:
                        break

    print(f"\nDownload complete. Total books now in folder: {len(used_titles)}")

if __name__ == "__main__":
    main()
