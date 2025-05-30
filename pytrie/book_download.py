import requests
from bs4 import BeautifulSoup
import os
import re

def sanitize_filename(filename):
    """
    Remove characters that are not safe for filenames.
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

# URL of the top books page on Project Gutenberg
url = "https://www.gutenberg.org/browse/scores/top"

# Create a directory to store the downloaded books
download_dir = "Gutenberg_Top_100"
os.makedirs(download_dir, exist_ok=True)

# Sets to keep track of downloaded book IDs and titles
downloaded_ids = set()
downloaded_titles = set()

# Fetch the top books page
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Gather all book links from the list.
book_links = soup.select("ol a[href^='/ebooks/']")

downloaded = 0

for link in book_links:
    if downloaded >= 100:
        break

    # Extract the book id and title
    book_id = link["href"].split("/")[-1]
    book_title = link.get_text(strip=True)
    safe_title = sanitize_filename(book_title)
    lower_title = safe_title.lower()

    # Skip if this title has already been downloaded (even if under a different ID)
    if lower_title in downloaded_titles:
        print(f"Skipping {book_title} (ID: {book_id}) because this title has already been processed.")
        continue

    # Check if the file already exists in the download directory
    file_path = os.path.join(download_dir, f"{safe_title}.txt")
    if os.path.exists(file_path):
        print(f"File for {book_title} (ID: {book_id}) already exists. Skipping download.")
        downloaded_titles.add(lower_title)
        downloaded_ids.add(book_id)
        downloaded += 1
        continue

    # Fetch the book's detail page to check for language
    details_url = f"https://www.gutenberg.org/ebooks/{book_id}"
    details_response = requests.get(details_url)
    details_soup = BeautifulSoup(details_response.text, "html.parser")

    # Look for the language metadata in the book details
    language_element = details_soup.find("th", string="Language")
    if language_element:
        language = language_element.find_next_sibling("td").get_text(strip=True)
        if "English" not in language:
            print(f"Skipping {book_title} (ID: {book_id}) because it's not in English.")
            downloaded_ids.add(book_id)
            continue
    else:
        print(f"Skipping {book_title} (ID: {book_id}) because language info not found.")
        downloaded_ids.add(book_id)
        continue

    # Form the URL for the plain text version
    book_text_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"

    # Attempt to download the book
    r = requests.get(book_text_url)
    if r.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(r.content)
        print(f"Downloaded: {book_title}")
        downloaded_ids.add(book_id)
        downloaded_titles.add(lower_title)
        downloaded += 1
    else:
        print(f"Failed to download {book_title} (ID: {book_id}), moving to next.")

print(f"Download complete. Total books downloaded: {downloaded}")