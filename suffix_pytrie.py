import pickle

class TrieNode:
    def __init__(self):
        self.children = {}
        self.leaf_id = None

class SuffixTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, leaf_id):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.leaf_id = leaf_id

    def get_leaf_id(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return node.leaf_id

def build_suffix_tree(words):
    trie = SuffixTrie()
    suffix_to_id = {}
    next_id = 1
    for word in words:
        trie.insert(word, next_id)
        suffix_to_id[word] = next_id
        next_id += 1
    return trie, suffix_to_id

def save_tree(trie, suffix_to_id):
    with open("suffix_tree.pkl", "wb") as f:
        pickle.dump((trie, suffix_to_id), f)

def load_tree():
    try:
        with open("suffix_tree.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None, None
