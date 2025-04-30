import datrie
import string
import pickle

def create_suffix_tree():
    """Creates a trie that accepts lowercase letters plus '#' and '$'."""
    allowed_chars = "#" + string.ascii_lowercase + "$"
    return datrie.Trie(allowed_chars)

def add_suffix(trie, suffix):
    """
    Adds a suffix to the trie if not already present.
    Returns True if added, False otherwise.
    """
    if suffix not in trie:
        trie[suffix] = True
        return True
    return False

def build_suffix_tree(word_list):
    """
    Build a trie containing every suffix of each word in word_list.
    For each word, we add:
      - The full word: "#word$"
      - Every proper suffix: "ord$", "rd$", ... (i.e. word[i:] + "$" for i>=1)
    Returns (trie, suffix_to_id):
      trie: the built trie
      suffix_to_id: dict mapping suffix -> leaf_id
    """
    trie = create_suffix_tree()
    suffix_to_id = {}
    current_id = 1

    for word in word_list:
        word = word.strip().lower()
        if word:
            # Full word entry with '#' at the beginning
            full_word = '#' + word + '$'
            if full_word not in suffix_to_id:
                if add_suffix(trie, full_word):
                    suffix_to_id[full_word] = current_id
                    current_id += 1
            # Proper suffixes (without the '#')
            for i in range(1, len(word) + 1):
                suffix = word[i:] + '$'
                if suffix not in suffix_to_id:
                    if add_suffix(trie, suffix):
                        suffix_to_id[suffix] = current_id
                        current_id += 1
    return trie, suffix_to_id

def save_tree(trie, mapping, filename="suffix_tree.pkl"):
    """Pickle (serialize) the trie and suffix→ID mapping to a file."""
    with open(filename, "wb") as f:
        pickle.dump((trie, mapping), f)
    print(f"Suffix tree and mapping saved to {filename}")

def load_tree(filename="suffix_tree.pkl"):
    try:
        with open(filename, "rb") as f:
            trie, mapping = pickle.load(f)
        print(f"Suffix tree and mapping loaded from {filename}")
        return trie, mapping
    except FileNotFoundError:
        print(f"File {filename} not found. Building Suffix Tree First.")
        return None, None
