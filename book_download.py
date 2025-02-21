import os
import re
import requests
import gutenbergpy
from bs4 import BeautifulSoup

# Directory to save books
SAVE_DIR = "gutenberg_top_books"
TOP_BOOKS_URL = "https://www.gutenberg.org/browse/scores/top"
NUM_BOOKS = 100

# Create directory if it doesn't exist
os.makedirs(SAVE_DIR, exist_ok=True)

def get_top_books():
    """Scrapes the top 100 books from Gutenberg and returns their IDs."""
    headers = {"User-Agent": "Mozilla/5.0"}  # Prevent request blocking
    response = requests.get(TOP_BOOKS_URL, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch top books list.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract book links only (ignore author links)
    book_links = [link["href"] for link in soup.find_all("a", href=re.compile(r"^/ebooks/\d+$"))]

    # Extract unique book IDs
    book_ids = list({int(re.search(r"/ebooks/(\d+)", link).group(1)) for link in book_links})

    return book_ids[:NUM_BOOKS]  # Get only the first 100 unique IDs

def download_book(book_id):
    """Downloads a book from Project Gutenberg using gutenbergpy and saves it as a text file."""
    try:
        raw_text = text = gutenbergpy.get_text_by_id(book_id) # Correct method
        text = raw_text(raw_text).decode("utf-8").strip()

        file_path = os.path.join(SAVE_DIR, f"book_{book_id}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Downloaded book {book_id}")

    except Exception as e:
        print(f"Error downloading book {book_id}: {e}")

# Get the top book IDs
top_books = get_top_books()

# Download each book
for book_id in top_books:
    download_book(book_id)

print("Download complete!")
