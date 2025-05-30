from collections import defaultdict
import os
import re
from .db_tree import get_or_create_book_id

# Splits text into (start, end) index tuples based on a fixed page size
def split_into_pages(text, page_size=1800):
    pages = []
    n = len(text)
    start = 0
    while start < n:
        end = min(start + page_size, n)
        # If we're not at a space, extend to the next space to avoid breaking a word
        if end < n and text[end] != " ":
            nxt = text.find(" ", end)
            end = nxt if nxt != -1 else n
        pages.append((start, end))
        start = end + 1  # Move to next page
    return pages

# Returns the actual page strings using the (start, end) ranges from split_into_pages
def get_book_pages(text, page_size=1500):
    bounds = split_into_pages(text, page_size)
    return [ text[start:end] for start, end in bounds ]


def index_books(folder, suffix_to_id, cursor, page_size=1500, filenames=None):
    occurrences_map = defaultdict(lambda: defaultdict(list))  # leaf_id -> book_id -> list of (page, offset)
    pages_map = {}  # book_id -> list of pages

    for filename in os.listdir(folder):
        if filenames and filename not in filenames:
            continue  # Skip if not in the provided filename list
        if not filename.endswith(".txt"):
            continue  # Only process .txt files

        path = os.path.join(folder, filename)
        print(filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().lower()  # Read and lowercase the entire text

        # Prepare paginated text for this book
        book_pages = get_book_pages(text, page_size)
        book_id = get_or_create_book_id(cursor, filename)  # Get or assign a unique book ID
        pages_map[book_id] = book_pages

        page_idx = 0  # Tracks current page index
        page_bounds = split_into_pages(text, page_size)  # Get page boundaries

        # Iterate through all word-like tokens in the text
        for match in re.finditer(r"\w+", text):
            token = match.group(0)
            char_pos = match.start()

            # Move to the correct page index if necessary
            while page_idx < len(page_bounds) - 1 and char_pos >= page_bounds[page_idx][1]:
                page_idx += 1
            page_no = page_idx + 1  # Pages are 1-based

            # Add full word match
            full_key = f"#{token}$"
            if full_key in suffix_to_id:
                leaf = suffix_to_id[full_key]
                occurrences_map[leaf][book_id].append((page_no, char_pos))  # Record occurrence

            # Add suffix matches
            for i in range(1, len(token) + 1):
                suffix = f"{token[i:]}$"
                if suffix in suffix_to_id:
                    leaf = suffix_to_id[suffix]
                    occurrences_map[leaf][book_id].append((page_no, char_pos + i))  # Offset starts from suffix position

    return occurrences_map, pages_map
#