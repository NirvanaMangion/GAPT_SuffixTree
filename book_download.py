import requests
from bs4 import BeautifulSoup
import os
import re

def sanitize_filename(filename):
    """
    Remove unsafe characters from filenames.
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

# URL of the top books page on Project Gutenberg
BASE_URL = "https://www.gutenberg.org"
TOP_BOOKS_URL = f"{BASE_URL}/browse/scores/top"

# Create a directory for storing downloaded books
DOWNLOAD_DIR = "Gutenberg_Top_100"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Track downloaded book IDs and titles
downloaded_books = set()

def get_existing_books():
    """
    Scans the download directory and adds existing books to `downloaded_books`
    to avoid duplicate downloads.
    """
    for file in os.listdir(DOWNLOAD_DIR):
        if file.endswith(".rtf"):
            downloaded_books.add(file.lower())  # Store lowercase filenames for case-insensitive matching

def fetch_top_books():
    """
    Fetches the top books page from Project Gutenberg and extracts book links.
    Returns a list of tuples (book_id, book_title, book_link).
    """
    response = requests.get(TOP_BOOKS_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # Gather all book links from the list
    book_links = soup.select("ol a[href^='/ebooks/']")
    books = []

    for link in book_links:
        book_id = link["href"].split("/")[-1]
        book_title = link.get_text(strip=True)
        books.append((book_id, book_title))

    return books

def get_book_language(book_id):
    """
    Fetches the book's detail page and extracts the language information.
    Returns language as a string, or none if not found.
    """
    details_url = f"{BASE_URL}/ebooks/{book_id}"
    details_response = requests.get(details_url)
    details_soup = BeautifulSoup(details_response.text, "html.parser")

    language_element = details_soup.find("th", string="Language")
    if language_element:
        return language_element.find_next_sibling("td").get_text(strip=True)
    return None

def download_book(book_id, book_title):
    """
    Downloads a book in plain text format if it's in English and not already downloaded.
    Saves it as an RTF file.
    """
    safe_title = sanitize_filename(book_title).lower()  # Normalize case for duplicate checking
    file_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.rtf")

    # Skip if the book is already downloaded
    if safe_title in downloaded_books:
        print(f"Skipping duplicate: {book_title} (ID: {book_id})")
        return False

    # Check book language
    language = get_book_language(book_id)
    if not language or "English" not in language:
        print(f"Skipping {book_title} (ID: {book_id}) - Not in English.")
        return False

    # Download book
    book_text_url = f"{BASE_URL}/cache/epub/{book_id}/pg{book_id}.txt"
    response = requests.get(book_text_url)

    if response.status_code == 200:
        book_text = response.text
        rtf_content = "{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0 Courier;}}\\f0\\fs20 " + book_text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}") + "}"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(rtf_content)
        
        downloaded_books.add(safe_title)
        print(f"Downloaded: {book_title}")
        return True
    else:
        print(f"Failed to download {book_title} (ID: {book_id})")
        return False

def main():
    """
    Main function to download the top 100 books without duplicates.
    """
    get_existing_books()  # Load already downloaded books
    top_books = fetch_top_books()

    downloaded_count = 0
    for book_id, book_title in top_books:
        if downloaded_count >= 100:
            break  # Stop after downloading 100 books

        if download_book(book_id, book_title):
            downloaded_count += 1

    print(f"Download complete. Total books downloaded: {downloaded_count}")

if __name__ == "__main__":
    main()
    