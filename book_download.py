import requests
from bs4 import BeautifulSoup
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

def clean_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    return re.sub(r'\s+', ' ', text).strip()

# URL of the top books page on Project Gutenberg
url = "https://www.gutenberg.org/browse/scores/top"
download_dir = "Gutenberg_Top_100"
os.makedirs(download_dir, exist_ok=True)

def fetch_book_links():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select("ol a[href^='/ebooks/']")

def download_book(book_id, book_title, existing_files):
    safe_title = sanitize_filename(book_title)
    lower_title = safe_title.lower()

    if lower_title in existing_files:
        print(f"Skipping {book_title} (ID: {book_id}) — already exists.")
        return False

    file_path = os.path.join(download_dir, f"{safe_title}.txt")

    try:
        details_url = f"https://www.gutenberg.org/ebooks/{book_id}"
        details_response = requests.get(details_url, timeout=10)
        details_soup = BeautifulSoup(details_response.text, "html.parser")

        language_element = details_soup.find("th", string="Language")
        if language_element:
            language = language_element.find_next_sibling("td").get_text(strip=True)
            if "English" not in language:
                print(f"Skipping {book_title} (ID: {book_id}) — not in English.")
                return False
        else:
            print(f"Skipping {book_title} (ID: {book_id}) — language unknown.")
            return False

        book_text_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
        r = requests.get(book_text_url, timeout=10)
        if r.status_code == 200:
            clean_content = clean_text(r.text)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(clean_content)
            print(f"Downloaded and cleaned: {book_title}")
            return lower_title  # Return the saved file's name
        else:
            print(f"Failed to download {book_title} (ID: {book_id})")
            return False
    except Exception as e:
        print(f"Error processing {book_title} (ID: {book_id}): {e}")
        return False

def main():
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

    with ThreadPoolExecutor(max_workers=10) as executor:
        while downloaded_count < total_needed and index < len(book_links):
            futures = []
            while len(futures) < 10 and index < len(book_links):
                link = book_links[index]
                book_id = link["href"].split("/")[-1]
                book_title = link.get_text(strip=True)
                futures.append(executor.submit(download_book, book_id, book_title, used_titles))
                index += 1

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
