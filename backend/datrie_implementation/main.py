import os
import re

from .suffix_tree import build_suffix_tree, save_tree, load_tree
from .db_tree import setup_database, store_occurrences, load_occurrences, get_or_create_book_id
from .moby_words import load_moby_words
from .index_books import index_books, split_into_pages

# Dictionary mapping emojis to their corresponding regex logic
EMOJI_REGEX_LITERATURE = {
    # Word Search
    "📄": {"description": "Ends with a suffix", "build": lambda arg: fr"{arg}$"},          # e.g., ment$
    "✏️": {"description": "Starts with a prefix", "build": lambda arg: fr"^{arg}"},         # e.g., ^un
    "📂": {"description": "Minimum word length", "build": lambda arg: fr"\b\w{{{arg},}}\b"}, # e.g., words >= N chars
    "📕": {"description": "Maximum word length", "build": lambda arg: fr"\b[a-zA-Z]{{1,{arg}}}\b"}, # e.g., words <= N chars
    "📏": {"description": "Exact word length", "build": lambda arg: fr"\b\w{{{arg}}}\b"},     # e.g., words = N chars
    "🖌️": {"description": "Ends in any listed suffix", "build": lambda arg: fr"({arg})$"},    # e.g., ed|ing$
    "📎": {"description": "Repeated characters", "build": lambda arg: fr"(.)\1{{{int(arg)-1},}}"}, # e.g., oo, ll
    "📖": {"description": "Exact word match", "build": lambda arg: fr"\b{arg}\b"},            # e.g., whole word
    "🔧": {"description": "Raw custom regex", "build": lambda arg: 'RAW_REGEX:' + arg},       # free-form regex
}

# Absolute path to the Gutenberg_Books directory
BOOK_FOLDER = os.path.abspath(
     os.path.join(os.path.dirname(__file__),
                  os.pardir,
                  os.pardir,
                  "Gutenberg_Books")
)

# Parses user emoji query into the appropriate regex pattern
def parse_emoji_regex(query):
    query = query.strip()  # remove whitespace
    for emoji in sorted(EMOJI_REGEX_LITERATURE, key=len, reverse=True):  # match longest emoji first
        prefix = emoji + ":"
        if query.startswith(prefix):
            raw_arg = query[len(prefix):].strip()  # get argument after emoji:
            arg = raw_arg  # no sentence logic anymore
            return EMOJI_REGEX_LITERATURE[emoji]["build"](arg)
    return None  # fallback if no emoji match

# Handles exact word searches using the suffix tree
def search_word(word, suffix_to_id, cursor):
    word = word.strip().lower()
    full_key = '#' + word + '$'  # format used in tree
    suffix_key = word + '$'
    keys_found = []

    if full_key in suffix_to_id:
        keys_found.append(full_key)
    if suffix_key in suffix_to_id:
        keys_found.append(suffix_key)

    if not keys_found:
        print(f"Suffix '{word}' not found in the tree.")
        return

    combined_occurrences = {}
    for key in keys_found:
        leaf_id = suffix_to_id[key]
        data = load_occurrences(cursor, leaf_id)
        for book_id, offsets in data.items():
            combined_occurrences.setdefault(book_id, []).extend(offsets)

    for book_id in combined_occurrences:
        combined_occurrences[book_id].sort()

    print(f"Results for '{word}':")
    for key in keys_found:
        matched = key.strip('$').lstrip('#')  # normalize word
        leaf_id = suffix_to_id[key]
        data = load_occurrences(cursor, leaf_id)
        for book_id, offsets in data.items():
            for page , pos in sorted(offsets):
                print(f"Book ID {book_id} — Page: {page} - Offset: {pos} — Matched: '{matched}'")
    print()

# Handles regex-based word searches
def search_regex(pattern, suffix_to_id, cursor):
    try:
        regex = re.compile(pattern)
    except re.error as e:
        print(f"Invalid regex pattern: {e}")
        return

    matching_keys = []
    for key in suffix_to_id:
        if key.endswith('$'):
            normalized = key[1:-1] if key.startswith('#') else key[:-1]
            if regex.search(normalized):
                matching_keys.append(key)

    if not matching_keys:
        print(f"No suffixes or words matching regex '{pattern}' found.")
        return

    combined_occurrences = {}
    for key in matching_keys:
        leaf_id = suffix_to_id[key]
        data = load_occurrences(cursor, leaf_id)
        for book_id, offsets in data.items():
            combined_occurrences.setdefault(book_id, []).extend(offsets)

    print(f"Regex Results for '{pattern}' — {len(matching_keys)} matching suffix-keys:")
    for key in matching_keys:
        matched = (key[1:-1] if key.startswith('#') else key[:-1])
        leaf_id = suffix_to_id[key]
        data = load_occurrences(cursor, leaf_id)
        for book_id, offsets in data.items():
            for page, pos in sorted(offsets):
                print(f"Book ID {book_id} — Page: {page} - Offset: {pos} — Matched: '{matched}'")
    print()
    return combined_occurrences

# Main function to run the CLI and manage interaction
def main():
    trie, suffix_to_id = load_tree()  # load prebuilt tree if available

    if trie is None:
        words = load_moby_words()  # load full dictionary
        trie, suffix_to_id = build_suffix_tree(words)
        print(f"Built suffix tree with {len(suffix_to_id)} unique suffixes.")
        save_tree(trie, suffix_to_id)  # persist tree
        conn, cursor = setup_database("leaves.db")
        occurrences_map, pages_map = index_books(BOOK_FOLDER, suffix_to_id, cursor)  # scan & index books
        print(f"Indexed {len(occurrences_map)} unique suffix occurrences.\nInserting into the database...")
        store_occurrences(cursor, occurrences_map)
        conn.commit()
    else:
        conn, cursor = setup_database("leaves.db")  # reuse DB if tree is already built

    while True:  # CLI loop
        print("\nWord Search Mode:")
        print("1️ Word Search")
        mode = input("Select 1 or exit: ").strip().lower()

        if mode in ["exit", "q"]:
            print("Characters returned to their stories. Session closed.")
            break

        if mode != "1":
            print("Invalid input. Please type 1 to continue.")
            continue

        # Show available emoji commands
        print("""
📚 Word Search Index

📄:<ending>        → Ends with a suffix (e.g. 📄:ment)
✏️:<prefix>        → Starts with a prefix (e.g. ✏️:un)
📂:<number>        → Words with at least this many letters (e.g. 📂:5)
📕:<number>        → Words with at most this many letters (e.g. 📕:3)
📏:<number>        → Words of exact length (e.g. 📏:6)
🖌️:<a|b|c>         → Ends in any of the listed suffixes (e.g. 🖌️:ed|ing)
📎:<number>        → Repeated characters (e.g. 📎:2 matches book, cool)
📖:<word>          → Exact word match (e.g. 📖:freedom)
🔧:<regex>         → Raw custom regex (e.g. 🔧:^[bcd].*ing$)
        """)

        query = input("Search Your Story: ").strip()
        if query.lower() in ["exit", "q", "quit"]:
            print("Characters returned to their stories. Session closed.")
            break

        pattern = parse_emoji_regex(query)
        if not pattern:
            print("Invalid word. Please use one of the listed emojis and formats.")
            continue

        # Route based on parsed pattern
        if pattern.startswith("RAW_REGEX:"):
            raw_pattern = pattern.split(":", 1)[1]
            search_regex(raw_pattern, suffix_to_id, cursor)
        elif query.startswith("📖:"):  # handle exact word match, but do NOT add dynamically
            word = query.split(":", 1)[1].strip()
            wl = word.lower()
            full_key = f"#{wl}$"

            if full_key not in suffix_to_id:
                print(f"Word “{word}” not found in the trie. Only words present during the original build are searchable.")
                continue
            search_word(word, suffix_to_id, cursor)
        else:
            search_regex(pattern, suffix_to_id, cursor)

    conn.close()  # cleanup DB connection

# Script execution starts here
if __name__ == "__main__":
    main()
