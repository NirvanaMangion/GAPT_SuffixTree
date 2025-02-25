import os
import re

def clean_text(text):
    """
    Convert text to lowercase and replace numbers & special symbols with spaces.
    """
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)  # Keep only letters and spaces
    return text

def process_downloaded_books(directory):
    """
    Process all text files in the given directory, clean the text, and overwrite the files.
    """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                cleaned_text = clean_text(text)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_text)
                print(f"Processed and cleaned: {filename}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

if __name__ == "__main__":
    download_dir = "Gutenberg_Top_100"
    if os.path.exists(download_dir):
        process_downloaded_books(download_dir)
    else:
        print(f"Directory '{download_dir}' does not exist.")
