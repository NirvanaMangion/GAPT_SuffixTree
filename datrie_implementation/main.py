import os
import re
from collections import defaultdict

from suffix_tree import build_suffix_tree, save_tree, load_tree
from db_tree import setup_database, get_or_create_book_id, store_occurrences, load_occurrences
from moby_words import load_moby_words
from sentence_search import search_sentences

EMOJI_REGEX_SPELLS = {
    # Word Search Spells
    "🪄": {"description": "Ends with a suffix", "build": lambda arg: fr"{arg}$"},
    "📜": {"description": "Starts with a prefix", "build": lambda arg: fr"^{arg}"},
    "🧺": {"description": "Minimum word length", "build": lambda arg: fr"^.{{{arg},}}$"},
    "🩶": {"description": "Maximum word length", "build": lambda arg: fr"^.{{1,{arg}}}$"},
    "🯞": {"description": "Exact word length", "build": lambda arg: fr"^.{{{arg}}}$"},
    "🔮": {"description": "Ends in any listed suffix", "build": lambda arg: fr"({arg})$"},
    "🕯️": {"description": "Repeated characters", "build": lambda arg: fr"(.)\1{{{int(arg)-1},}}"},
    "📖": {"description": "Exact word match", "build": lambda arg: fr"\b{arg}\b"},
    "🔧": {"description": "Raw custom regex", "build": lambda arg: 'RAW_REGEX:' + arg},

    # Sentence Search Spells
    "📝": {"description": "Exact sentence phrase", "build": lambda arg: 'SENTENCE:' + arg},
    "🔮S": {"description": "Sentence starts with", "build": lambda arg: 'SENTENCE_REGEX:^' + arg},
    "🎽": {"description": "Sentence ends with", "build": lambda arg: 'SENTENCE_REGEX:' + arg + '$'},
    "🔍": {"description": "Sentence contains word", "build": lambda arg: 'SENTENCE_REGEX:\\b' + arg + '\\b'},
    "🎭": {"description": "Sentence contains any of listed words", "build": lambda arg: 'SENTENCE_REGEX:' + arg},
    "🧙": {"description": "Structured sentence pattern", "build": lambda arg: 'SENTENCE_REGEX:' + arg},
    "🔧S": {"description": "Raw sentence regex", "build": lambda arg: 'SENTENCE_REGEX:' + arg}
}

def parse_emoji_regex(query):
    if ':' not in query:
        return None
    emoji, arg = query.split(':', 1)
    arg = arg.strip().lower()
    spell = EMOJI_REGEX_SPELLS.get(emoji)
    if not spell:
        return None
    return spell["build"](arg)

def build_sentence_map(folder):
    sentence_map = {}
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
                text = f.read()
            sentences = re.split(r'[.!?]', text)
            sentence_map[filename] = [s.strip() for s in sentences if s.strip()]
    return sentence_map

def index_books(folder, suffix_to_id, cursor):
    occurrences_map = defaultdict(lambda: defaultdict(list))
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder, filename)
            print(f"Indexing {filename} ...")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                print(f"Failed to read {filename}: {e}")
                continue
            book_id = get_or_create_book_id(cursor, filename)
            tokens = re.findall(r"\w+", text.lower())
            for token_index, token in enumerate(tokens):
                full_word = '#' + token + '$'
                leaf_id = suffix_to_id.get(full_word)
                if leaf_id:
                    occurrences_map[leaf_id][book_id].append(token_index)
                for i in range(1, len(token) + 1):
                    suffix = token[i:] + '$'
                    leaf_id = suffix_to_id.get(suffix)
                    if leaf_id:
                        occurrences_map[leaf_id][book_id].append(token_index + i)
    return occurrences_map

def search_word(word, suffix_to_id, cursor):
    word = word.strip().lower()
    full_key = '#' + word + '$'
    suffix_key = word + '$'
    keys_found = []

    if full_key in suffix_to_id:
        keys_found.append(full_key)
    if suffix_key in suffix_to_id:
        keys_found.append(suffix_key)

    if not keys_found:
        print(f"❌ Suffix '{word}' not found in the tree.")
        return

    combined_occurrences = {}
    for key in keys_found:
        leaf_id = suffix_to_id[key]
        data = load_occurrences(cursor, leaf_id)
        for book_id, offsets in data.items():
            combined_occurrences.setdefault(book_id, []).extend(offsets)

    for book_id in combined_occurrences:
        combined_occurrences[book_id].sort()

    print(f"📚 Results for '{word}':")
    for book_id, offsets in combined_occurrences.items():
        print(f"📘 Book ID {book_id} — Offsets: ({', '.join(map(str, offsets))}), Count: {len(offsets)}\n")

def search_regex(pattern, suffix_to_id, cursor):
    try:
        regex = re.compile(pattern)
    except re.error as e:
        print(f"❌ Invalid regex pattern: {e}")
        return

    matching_keys = []
    for key in suffix_to_id:
        if key.endswith('$'):
            normalized = key[1:-1] if key.startswith('#') else key[:-1]
            if regex.search(normalized):
                matching_keys.append(key)

    if not matching_keys:
        print(f"❌ No suffixes or words matching regex '{pattern}' found.")
        return

    combined_occurrences = {}
    for key in matching_keys:
        leaf_id = suffix_to_id[key]
        data = load_occurrences(cursor, leaf_id)
        for book_id, offsets in data.items():
            combined_occurrences.setdefault(book_id, []).extend(offsets)

    for book_id in combined_occurrences:
        combined_occurrences[book_id].sort()

    print(f"🔎 Regex Results for '{pattern}' — Matches: {len(matching_keys)} keys")
    for book_id, offsets in combined_occurrences.items():
        print(f"📘 Book ID {book_id} — Offsets: ({', '.join(map(str, offsets))}), Count: {len(offsets)}\n")

def main():
    trie, suffix_to_id = load_tree()
    if trie is None:
        words = load_moby_words()
        trie, suffix_to_id = build_suffix_tree(words)
        print(f"Built suffix tree with {len(suffix_to_id)} unique suffixes.")
        save_tree(trie, suffix_to_id)
        conn, cursor = setup_database("leaves.db")
        folder = "Gutenberg_Top_100"
        occurrences_map = index_books(folder, suffix_to_id, cursor)
        print(f"Indexed {len(occurrences_map)} unique suffix occurrences.\nInserting into the database...")
        store_occurrences(cursor, occurrences_map)
        conn.commit()
    else:
        conn, cursor = setup_database("leaves.db")

    folder = "Gutenberg_Top_100"
    sentence_map = build_sentence_map(folder)

    while True:
        print("\n🧭 Choose your search mode:")
        print("1️⃣ Word Search")
        print("2️⃣ Sentence Search")
        mode = input("Select 1 or 2 (or 'exit'): ").strip().lower()

        if mode in ["exit", "q"]:
            print("🕯️ Scrolls returned to the archive. Session closed.")
            break

        if mode not in ["1", "2"]:
            print("❌ Invalid input. Please type 1 or 2 to continue.")
            continue

        if mode == "1":
            print("""
📚 Word Search Spellbook

🪄:<ending>        → Ends with a suffix (e.g. 🪄:ment)
📜:<prefix>        → Starts with a prefix (e.g. 📜:un)
🧺:<number>        → Words with at least this many letters (e.g. 🧺:5)
🩶:<number>        → Words with at most this many letters (e.g. 🩶:3)
🯞:<number>        → Words of exact length (e.g. 🯞:6)
🔮:<a|b|c>         → Ends in any of the listed suffixes (e.g. 🔮:ed|ing)
🕯️:<number>        → Repeated characters (e.g. 🕯️:2 matches book, cool)
📖:<word>          → Exact word match (e.g. 📖:freedom)
🔧:<regex>         → Raw custom regex (e.g. 🔧:^[bcd].*ing$)
            """)
        else:
            print("""
📝 Sentence Search Spellbook

📝:<phrase>        → Exact sentence phrase match (e.g. 📝:it was the best of times)
🔮S:<word>         → Sentence starts with word (e.g. 🔮S:freedom)
🎽:<word>          → Sentence ends with word (e.g. 🎽:truth)
🔍:<word>          → Sentence contains the exact word (e.g. 🔍:love)
🎭:<a|b|c>         → Sentence contains any listed word (e.g. 🎭:life|death|hope)
🧙:<pattern>       → Sentence with structure pattern (e.g. 🧙:[A-Z][^.!?]*war)
🔧S:<regex>        → Raw custom sentence regex (e.g. 🔧S:^The.*end$)
            """)

        query = input("✨ Cast your spell: ").strip()
        if query.lower() in ["exit", "q", "quit"]:
            print("🕯️ Scrolls returned to the archive. Session closed.")
            break

        pattern = parse_emoji_regex(query)
        if not pattern:
            print("❌ Invalid spell. Please use one of the listed emojis and formats.")
            continue

        if pattern.startswith("SENTENCE_REGEX:"):
            regex = pattern.split(":", 1)[1]
            search_sentences(regex, sentence_map, use_regex=True)
        elif pattern.startswith("SENTENCE:"):
            phrase = pattern.split(":", 1)[1]
            search_sentences(phrase, sentence_map, use_regex=False)
        elif pattern.startswith("RAW_REGEX:"):
            raw_pattern = pattern.split(":", 1)[1]
            search_regex(raw_pattern, suffix_to_id, cursor)
        else:
            search_regex(pattern, suffix_to_id, cursor)

    conn.close()

if __name__ == "__main__":
    main()
