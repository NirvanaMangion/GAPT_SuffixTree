import requests
from bs4 import BeautifulSoup
import os
import re

def sanitize_filename(filename):
    """
    Remove characters that are not safe for filenames.
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()

def clean_text(text):
    """Convert to lowercase, remove special characters & numbers, normalize spaces."""
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())  # Remove non-letters, keep spaces
    return re.sub(r'\s+', ' ', text).strip()  # Normalize spaces

# URL of the top books page on Project Gutenberg
url = "https://www.gutenberg.org/browse/scores/top"

download_dir = "Gutenberg_Top_100"
os.makedirs(download_dir, exist_ok=True)

existing_files = {sanitize_filename(f).lower() for f in os.listdir(download_dir) if f.endswith(".txt")}

def fetch_book_links():
    """Fetch book links from the top books page."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select("ol a[href^='/ebooks/']")

def download_book(book_id, book_title):
    """Download a single book given its ID and title."""
    safe_title = sanitize_filename(book_title)
    lower_title = safe_title.lower()
    
    if lower_title in existing_files:
        print(f"Skipping {book_title} (ID: {book_id}) because this title has already been processed.")
        return False
    
    file_path = os.path.join(download_dir, f"{safe_title}.txt")
    
    details_url = f"https://www.gutenberg.org/ebooks/{book_id}"
    details_response = requests.get(details_url)
    details_soup = BeautifulSoup(details_response.text, "html.parser")
    
    language_element = details_soup.find("th", string="Language")
    if language_element:
        language = language_element.find_next_sibling("td").get_text(strip=True)
        if "English" not in language:
            print(f"Skipping {book_title} (ID: {book_id}) because it's not in English.")
            return False
    else:
        print(f"Skipping {book_title} (ID: {book_id}) because language info not found.")
        return False
    
    book_text_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    r = requests.get(book_text_url)
    if r.status_code == 200:
        clean_content = clean_text(r.text)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_content)
        print(f"Downloaded and cleaned: {book_title}")
        return True
    else:
        print(f"Failed to download {book_title} (ID: {book_id}), moving to next.")
        return False

def main():
    """Main function to handle downloading books sequentially."""
    book_links = fetch_book_links()
    downloaded_count = 0
    
    for link in book_links:
        if downloaded_count + len(existing_files) >= 100:
            break
        
        book_id = link["href"].split("/")[-1]
        book_title = link.get_text(strip=True)
        
        if download_book(book_id, book_title):
            downloaded_count += 1
    
    print(f"Download complete. Total books downloaded: {downloaded_count}")

if __name__ == "__main__":
    main()
