from moby_words import load_moby_words
import pickle
import os
import sys

class SuffixTreeNode:
    def __init__(self, start, end):
        self.children = {}  # Maps characters to child nodes.
        self.suffix_link = None
        self.start = start
        self.end = end  # For leaves, end is a reference (list) to the global end.
        self.index = -1  # For leaf nodes, this can store the starting index of the suffix.

        # Augmentation: Track word offsets and frequencies
        self.positions = []  # Stores word start positions (offsets)
        self.word_frequencies = {}  # Stores word frequency counts

    def edge_length(self, current_position):
        if isinstance(self.end, list):
            return self.end[0] - self.start + 1
        else:
            return self.end - self.start + 1

    def __getstate__(self):
        """Prepare the object for pickling."""
        state = self.__dict__.copy()
        if isinstance(self.end, list):
            state["end"] = self.end[0]  
        return state

    def __setstate__(self, state):
        """Restore the object after unpickling."""
        self.__dict__.update(state)
        if isinstance(self.end, int):
            self.end = [self.end]  

class SuffixTree:
    def __init__(self, text):
        self.text = text
        self.size = len(text)
        self.root = SuffixTreeNode(-1, -1)
        self.root.suffix_link = self.root

        self.active_node = self.root
        self.active_edge = -1
        self.active_length = 0

        self.remaining_suffix_count = 0
        self.leaf_end = -1  
        self.last_new_node = None

        self.build_tree()
        self.set_suffix_index_by_dfs(self.root, 0)

    def save_to_file(self, filename):
        """Pickle the suffix tree to a file."""
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load_from_file(filename):
        """Load a pickled suffix tree from a file."""
        if not os.path.exists(filename):
            return None
        with open(filename, "rb") as f:
            tree = pickle.load(f)
        sys.setrecursionlimit(10**6)
        return tree

    def build_tree(self):
        for pos in range(self.size):
            self.extend_suffix_tree(pos)

    def extend_suffix_tree(self, pos):
        self.leaf_end = pos
        self.remaining_suffix_count += 1
        self.last_new_node = None

        while self.remaining_suffix_count > 0:
            if self.active_length == 0:
                self.active_edge = pos

            current_char = self.text[self.active_edge]

            if current_char not in self.active_node.children:
                new_leaf = SuffixTreeNode(pos, self.leaf_end)
                new_leaf.positions.append(pos)
                word = self.extract_word(pos)
                if word:
                    new_leaf.word_frequencies[word] = new_leaf.word_frequencies.get(word, 0) + 1
                self.active_node.children[current_char] = new_leaf

                if self.last_new_node is not None:
                    self.last_new_node.suffix_link = self.active_node
                    self.last_new_node = None
            else:
                next_node = self.active_node.children[current_char]
                edge_length = next_node.edge_length(pos)

                if self.active_length >= edge_length:
                    self.active_edge += edge_length
                    self.active_length -= edge_length
                    self.active_node = next_node
                    continue

                if self.text[next_node.start + self.active_length] == self.text[pos]:
                    if self.last_new_node is not None and self.active_node != self.root:
                        self.last_new_node.suffix_link = self.active_node
                        self.last_new_node = None
                    self.active_length += 1
                    break

                split_end = next_node.start + self.active_length - 1
                split_node = SuffixTreeNode(next_node.start, split_end)
                self.active_node.children[current_char] = split_node

                next_node.start += self.active_length
                split_node.children[self.text[next_node.start]] = next_node

                new_leaf = SuffixTreeNode(pos, self.leaf_end)
                new_leaf.positions.append(pos)
                word = self.extract_word(pos)
                if word:
                    new_leaf.word_frequencies[word] = new_leaf.word_frequencies.get(word, 0) + 1
                split_node.children[self.text[pos]] = new_leaf

                if self.last_new_node is not None:
                    self.last_new_node.suffix_link = split_node

                self.last_new_node = split_node

            self.remaining_suffix_count -= 1

            if self.active_node == self.root and self.active_length > 0:
                self.active_length -= 1
                self.active_edge = pos - self.remaining_suffix_count + 1
            elif self.active_node != self.root:
                self.active_node = self.active_node.suffix_link if self.active_node.suffix_link is not None else self.root

    def set_suffix_index_by_dfs(self, node, label_height):
        if not node:
            return
        if len(node.children) == 0:
            node.index = self.size - label_height
            return
        for child in node.children.values():
            self.set_suffix_index_by_dfs(child, label_height + child.edge_length(self.leaf_end))

    def extract_word(self, pos):
        end_pos = pos
        while end_pos < len(self.text) and self.text[end_pos] != "#":
            end_pos += 1
        return self.text[pos:end_pos] if end_pos > pos else None

    def search_with_offsets(self, pattern):
        current_node = self.root
        i = 0

        while i < len(pattern):
            if pattern[i] not in current_node.children:
                return None  

            child = current_node.children[pattern[i]]
            edge_length = child.edge_length(self.leaf_end)
            label = self.text[child.start: child.start + edge_length]

            j = 0
            while j < len(label) and i < len(pattern):
                if pattern[i] != label[j]:
                    return None  
                i += 1
                j += 1

            current_node = child  

        positions = []
        word_frequency = 0

        def collect_positions(node):
            nonlocal word_frequency
            if node.index != -1:  
                positions.extend(node.positions)
                word_frequency += node.word_frequencies.get(pattern, 0)
            for child in node.children.values():
                collect_positions(child)

        collect_positions(current_node)

        valid_positions = []
        for pos in positions:
            if (pos == 0 or self.text[pos - 1] == '#') and \
                (pos + len(pattern) == len(self.text) or self.text[pos + len(pattern)] in ('#', '$')):
                valid_positions.append(pos)

        if not valid_positions:
            return None

        return {
            "positions": valid_positions,
            "frequency": len(valid_positions)
        }

if __name__ == '__main__':
    filename = "suffix_tree.pkl"

    suffix_tree = SuffixTree.load_from_file(filename)
    
    if suffix_tree is None:
        words = load_moby_words()
        corpus_text = "#".join(word.lower() for word in words) + "$"
        suffix_tree = SuffixTree(corpus_text)
        suffix_tree.save_to_file(filename)

    while True:
        search_term = input("\nEnter a word to search (or type 'exit' to quit): ").strip().lower()
        if search_term == "exit":
            break

        result = suffix_tree.search_with_offsets(search_term)
        if result and result["frequency"] > 0:
            print(f"Yes, '{search_term}' is found!")
            print(f"   - Positions: {result['positions']}")
            print(f"   - Frequency: {result['frequency']}")
        else:
            print(f"No, '{search_term}' is not found.")
