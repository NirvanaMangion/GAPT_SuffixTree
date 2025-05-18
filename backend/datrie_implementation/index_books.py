# index_books.py

from collections import defaultdict
import os
import re
from db_tree import get_or_create_book_id

def split_into_pages(text, page_size=1500):
    """
    Returns a list of (start, end) indices for each page,
    each at least `page_size` chars long, but stretched to
    the next space so words aren't split.
    """
    pages = []
    n = len(text)
    start = 0
    while start < n:
        end = min(start + page_size, n)
        if end < n and text[end] != " ":
            nxt = text.find(" ", end)
            end = nxt if nxt != -1 else n
        pages.append((start, end))
        start = end + 1
    return pages

def get_book_pages(text, page_size=1500):
    """
    Cut `text` into ~page_size-char chunks, extending to the next space
    so you never split words. Returns a list of page-strings.
    """
    bounds = split_into_pages(text, page_size)
    return [ text[start:end] for start, end in bounds ]

def index_books(folder, suffix_to_id, cursor, page_size=1500, filenames=None):
    """
    Tokenizes each book, and for each token match,
    finds its page by advancing a page_idx pointer.
    Records (page_no, char_offset) for each suffix occurrence.
    Also builds a pages_map so the frontend can fetch the raw text.
    Returns:
      occurrences_map: { leaf_id: { book_id: [ (page_no, offset), … ] } }
      pages_map:       { book_id: [ page1_text, page2_text, … ] }
    """
    occurrences_map = defaultdict(lambda: defaultdict(list))
    pages_map       = {}

    for filename in os.listdir(folder):
        if filenames and filename not in filenames:
            continue
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(folder, filename)
        with open(path, "r", encoding="latin-1") as f:
            text = f.read().lower()

        # create page-text slices for frontend
        book_pages = get_book_pages(text, page_size)
        book_id    = get_or_create_book_id(cursor, filename)
        pages_map[book_id] = book_pages

        # now index tokens as before
        page_idx = 0
        page_bounds = split_into_pages(text, page_size)
        for match in re.finditer(r"\w+", text):
            token    = match.group(0)
            char_pos = match.start()

            # advance to the correct page
            while page_idx < len(page_bounds)-1 and char_pos >= page_bounds[page_idx][1]:
                page_idx += 1
            page_no = page_idx + 1  # 1-based

            # full word key
            full_key = f"#{token}$"
            if full_key in suffix_to_id:
                leaf = suffix_to_id[full_key]
                occurrences_map[leaf][book_id].append((page_no, char_pos))

            # proper suffixes
            for i in range(1, len(token)+1):
                suffix = f"{token[i:]}$"
                if suffix in suffix_to_id:
                    leaf = suffix_to_id[suffix]
                    occurrences_map[leaf][book_id].append((page_no, char_pos + i))

    return occurrences_map, pages_map
