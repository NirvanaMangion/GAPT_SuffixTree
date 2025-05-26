import datrie
import string
import pickle

# Create a datrie Trie that supports lowercase letters, #, and $
def create_suffix_tree():
    allowed_chars = "#" + string.ascii_lowercase + "$"
    return datrie.Trie(allowed_chars)


# Add a suffix to the trie if it's not already present
def add_suffix(trie, suffix):
    if suffix not in trie:
        trie[suffix] = True
        return True
    return False

# Build suffix tree and map each suffix to a unique ID
def build_suffix_tree(word_list):
    trie = create_suffix_tree()
    suffix_to_id = {}
    current_id = 1

    for word in word_list:
        word = word.strip().lower()
        if word:
            full_word = '#' + word + '$'  # special marker for full word
            if full_word not in suffix_to_id:
                if add_suffix(trie, full_word):
                    suffix_to_id[full_word] = current_id
                    current_id += 1


            # Add proper suffixes (excluding the first character)
            for i in range(1, len(word) + 1):
                suffix = word[i:] + '$'
                if suffix not in suffix_to_id:
                    if add_suffix(trie, suffix):
                        suffix_to_id[suffix] = current_id
                        current_id += 1

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
