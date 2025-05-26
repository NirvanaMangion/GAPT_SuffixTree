import os
import requests
import zipfile

# URLs and file paths
MOBY_WORDS_ZIP_URL = "https://github.com/dwyl/english-words/archive/refs/heads/master.zip"
MOBY_WORDS_ZIP_FILE = "moby_words.zip"
MOBY_WORDS_FILE = "moby_words.txt"
EXTRACTED_DIR = "english-words-master"

# Download and extract word list if not present
def download_moby_words():
    if not os.path.exists(MOBY_WORDS_FILE):
        print(f"Downloading Moby Words dataset from {MOBY_WORDS_ZIP_URL}...")

        response = requests.get(MOBY_WORDS_ZIP_URL, stream=True)
        if response.status_code == 200:
            with open(MOBY_WORDS_ZIP_FILE, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print("Download complete.")

            # Extract zip
            with zipfile.ZipFile(MOBY_WORDS_ZIP_FILE, 'r') as zip_ref:
                zip_ref.extractall(".")

            # Rename extracted file
            extracted_file = os.path.join(EXTRACTED_DIR, "words_alpha.txt")
            if os.path.exists(extracted_file):
                os.rename(extracted_file, MOBY_WORDS_FILE)
                print(f"Extracted word list to {MOBY_WORDS_FILE}")
            else:
                print("Error: words_alpha.txt not found.")
        else:
            print(f"Failed to download. Status Code: {response.status_code}")

# Load and clean word list
def load_moby_words():
    download_moby_words()
    if os.path.exists(MOBY_WORDS_FILE):
        print("Reading words...")
        with open(MOBY_WORDS_FILE, 'r', encoding='utf-8') as f:
            words = f.read().splitlines()

        # Deduplicate and lowercase
        words = list(set(word.strip().lower() for word in words if word.strip()))
        print(f"Total words loaded: {len(words)}")
        return words
    else:
        print("Error: Moby Words file not found.")
        return []

# Run as script
if __name__ == "__main__":
    print("Running as standalone script...")
    words = load_moby_words()
    print(f"First 10 words: {words[:10]}")
