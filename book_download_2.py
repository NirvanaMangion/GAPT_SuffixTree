import requests
from bs4 import BeautifulSoup
import os

# URL of the top 100 books list
url = "https://www.gutenberg.org/browse/scores/top"

# Create a directory for books
os.makedirs("Gutenberg_Top_100", exist_ok=True)

# Fetch the top books page
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Find the list of books
book_links = []
for link in soup.select("ol a[href^='/ebooks/']")[:100]:  # Get top 100
    book_id = link["href"].split("/")[-1]
    book_links.append(f"https://www.gutenberg.org/ebooks/{book_id}")

# Download books
for book_url in book_links:
    book_id = book_url.split("/")[-1]
    book_text_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"

    book_response = requests.get(book_text_url)

    if book_response.status_code == 200:
        with open(f"Gutenberg_Top_100/{book_id}.txt", "wb") as file:
            file.write(book_response.content)
        print(f"Downloaded: {book_id}")
    else:
        print(f"Failed: {book_id}")

print("Download complete.")
