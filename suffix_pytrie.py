import re
import pickle
from pytrie import StringTrie

def clean_text(text):
    # Removes punctuation, capitalization, and special characters.
    return re.findall(r"\b[a-z]+\b", text.lower())

def create_suffix_tree():
    # new empty suffix trie.
    return StringTrie()

def add_suffix(trie, suffix):
    # Adds a suffix to the trie if it doesn't already exist.
    if suffix not in trie:
        trie[suffix] = True
        return True
    return False

def build_suffix_tree(word_list):
    
    # Building the suffix tree

    trie = create_suffix_tree()
    suffix_to_id = {}
    current_id = 1

    for word in word_list:
        word = word.strip().lower()
        if word:
            for i in range(len(word)):
                suffix = word[i:]
                if suffix not in suffix_to_id:
                    if add_suffix(trie, suffix):
                        suffix_to_id[suffix] = current_id
                        current_id += 1
    return trie, suffix_to_id


def save_tree(trie, mapping, filename="suffix_tree.pkl"):
    # Saves the trie and mapping to a file.

    with open(filename, "wb") as f:
        pickle.dump((trie, mapping), f)

def load_tree(filename="suffix_tree.pkl"):
    # Loads the trie and mapping from a file.
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("Suffix tree file not found. Please build the tree first.")
        return None, None

