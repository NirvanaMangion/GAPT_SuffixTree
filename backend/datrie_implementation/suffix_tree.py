import datrie
import string
import pickle

# Create a datrie Trie that supports lowercase letters, #, and $
def create_suffix_tree():
    allowed_chars = "#" + string.ascii_lowercase + "$"
    return datrie.Trie(allowed_chars)

# Optimized: Build suffix tree and map each suffix to a unique ID, deduplicating all suffixes first
def build_suffix_tree(word_list):
    trie = create_suffix_tree()
    suffix_to_id = {}
    all_suffixes = set()  # Deduplicate all suffixes before inserting

    # Gather all unique suffixes (including full words with special marker)
    for word in word_list:
        word = word.strip().lower()
        if word:
            all_suffixes.add('#' + word + '$')  # special marker for full word
            all_suffixes.update(word[i:] + '$' for i in range(1, len(word) + 1))

    # Now insert all unique suffixes into trie and assign IDs
    for current_id, suffix in enumerate(all_suffixes, 1):
        trie[suffix] = True
        suffix_to_id[suffix] = current_id

    return trie, suffix_to_id

# Save trie and mapping to a pickle file
def save_tree(trie, mapping, filename="suffix_tree.pkl"):
    with open(filename, "wb") as f:
        pickle.dump((trie, mapping), f)
    print(f"Suffix tree and mapping saved to {filename}")

# Load trie and mapping from a pickle file
def load_tree(filename="suffix_tree.pkl"):
    try:
        with open(filename, "rb") as f:
            trie, mapping = pickle.load(f)
        print(f"Suffix tree and mapping loaded from {filename}")
        return trie, mapping
    except FileNotFoundError:
        print(f"File {filename} not found. Building Suffix Tree First.")
        return None, None
