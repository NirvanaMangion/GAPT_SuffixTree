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


def index_books(folder, suffix_to_id, cursor, page_size=1500):
    """
    Tokenizes each book, and for each token match,
    finds its page by advancing a page_idx pointer.
    Records (page_no, char_offset) for each suffix occurrence.
    """

    occurrences_map = defaultdict(lambda: defaultdict(list))

    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().lower()

        # build page boundaries
        pages = split_into_pages(text, page_size)

        book_id = get_or_create_book_id(cursor, filename)
        page_idx = 0

        for match in re.finditer(r"\w+", text):
            token    = match.group(0)
            char_pos = match.start()

            # advance page_idx until char_pos falls inside pages[page_idx]
            while page_idx < len(pages)-1 and char_pos >= pages[page_idx][1]:
                page_idx += 1
            page_no = page_idx + 1  # 1-based page number

            # full word
            full_key = f"#{token}$"
            if full_key in suffix_to_id:
                leaf = suffix_to_id[full_key]
                occurrences_map[leaf][book_id].append((page_no, char_pos))

            # proper suffixes
            for i in range(1, len(token)+1):
                suffix = f"{token[i:]}$"
                if suffix in suffix_to_id:
                    leaf = suffix_to_id[suffix]
                    # offset of the start of that suffix is char_pos + i
                    occurrences_map[leaf][book_id].append((page_no, char_pos + i))

    return occurrences_map
