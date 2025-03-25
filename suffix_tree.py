import pygtrie
import pickle

class SuffixTree:
    def __init__(self):
        """Creates an empty suffix tree using pygtrie."""
        self.trie = pygtrie.CharTrie()

    def add_suffix(self, suffix, suffix_id):
        """Adds a suffix to the trie if it does not already exist."""
        if suffix not in self.trie:
            self.trie[suffix] = suffix_id
            return True
        return False

def build_suffix_tree(word_list):
    """Builds a suffix tree from a given list of words."""
    suffix_tree = SuffixTree()
    suffix_to_id = {}
    current_id = 1
    
    for word in word_list:
        word = word.strip().lower()
        if word:
            for i in range(len(word)):
                suffix = word[i:]
                if suffix not in suffix_to_id:
                    if suffix_tree.add_suffix(suffix, current_id):
                        suffix_to_id[suffix] = current_id
                        current_id += 1
    
    return suffix_tree, suffix_to_id

def save_tree(suffix_tree, mapping, filename="suffix_tree.pkl"):
    """Saves the suffix tree and mapping to a file."""
    with open(filename, "wb") as f:
        pickle.dump((suffix_tree.trie, mapping), f)

def load_tree(filename="suffix_tree.pkl"):
    """Loads the suffix tree and mapping from a file."""
    with open(filename, "rb") as f:
        trie, mapping = pickle.load(f)
        suffix_tree = SuffixTree()
        suffix_tree.trie = trie
        return suffix_tree, mapping
