from moby_words import load_moby_words
import pickle
import os
import sys

class SuffixTreeNode:
    def __init__(self, start, end):
        self.children = {}       # Maps characters to child nodes.
        self.suffix_link = None
        self.start = start       # Start index of the edge label in the text.
        self.end = end           # For leaves, end is a reference (list) to the global end.
        self.index = -1          # For leaf nodes, stores the starting index of the suffix.

        # Augmentation: Track word start positions and word frequencies.
        self.positions = []      # Stores word start positions (offsets) for occurrences.
        self.word_frequencies = {}  # Stores word frequency counts for the substring.

    def edge_length(self, current_position):
        # For leaves, self.end is a reference to a list (global end).
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
        self.text = text          # The input text (should be preprocessed as needed).
        self.size = len(text)
        self.root = SuffixTreeNode(-1, -1)
        self.root.suffix_link = self.root

        # Active point for Ukkonen's algorithm.
        self.active_node = self.root
        self.active_edge = -1
        self.active_length = 0

        self.remaining_suffix_count = 0
        self.leaf_end = -1        # Global end value (as a mutable list for leaves).
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
        # Increase recursion limit in case of deep trees.
        sys.setrecursionlimit(10**6)
        return tree

    def build_tree(self):
        """Construct the suffix tree using Ukkonen's algorithm."""
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

            # Case 1: No edge starting with current_char from active_node.
            if current_char not in self.active_node.children:
                new_leaf = SuffixTreeNode(pos, self.leaf_end)
                new_leaf.positions.append(pos)
                # Augment with word frequency using extract_word.
                word = self.extract_word(pos)
                if word:
                    new_leaf.word_frequencies[word] = new_leaf.word_frequencies.get(word, 0) + 1
                self.active_node.children[current_char] = new_leaf

                # Suffix link update.
                if self.last_new_node is not None:
                    self.last_new_node.suffix_link = self.active_node
                    self.last_new_node = None
            else:
                next_node = self.active_node.children[current_char]
                edge_length = next_node.edge_length(pos)

                # If active_length is greater than current edge length, walk down.
                if self.active_length >= edge_length:
                    self.active_edge += edge_length
                    self.active_length -= edge_length
                    self.active_node = next_node
                    continue

                # Case 2: Next character in edge is same as current character.
                if self.text[next_node.start + self.active_length] == self.text[pos]:
                    if self.last_new_node is not None and self.active_node != self.root:
                        self.last_new_node.suffix_link = self.active_node
                        self.last_new_node = None
                    self.active_length += 1
                    break

                # Case 3: Split the edge.
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

            # Update the active point.
            if self.active_node == self.root and self.active_length > 0:
                self.active_length -= 1
                self.active_edge = pos - self.remaining_suffix_count + 1
            elif self.active_node != self.root:
                self.active_node = self.active_node.suffix_link if self.active_node.suffix_link is not None else self.root

    def set_suffix_index_by_dfs(self, node, label_height):
        """Assign suffix indexes to leaf nodes via DFS traversal."""
        if not node:
            return
        if len(node.children) == 0:
            node.index = self.size - label_height
            return
        for child in node.children.values():
            self.set_suffix_index_by_dfs(child, label_height + child.edge_length(self.leaf_end))

    def extract_word(self, pos):
        """
        Extracts a word from the text starting at pos until a '#' delimiter is found.
        This assumes words are delimited by '#' and the text ends with '$'.
        """
        end_pos = pos
        while end_pos < len(self.text) and self.text[end_pos] != "#":
            end_pos += 1
        return self.text[pos:end_pos] if end_pos > pos else None

    def search_with_offsets(self, pattern):
        current_node = self.root
        i = 0
        print(f"Starting search for pattern: '{pattern}'")
        # Traverse the tree according to the pattern.
        while i < len(pattern):
            print(f"At node with children: {list(current_node.children.keys())}, looking for '{pattern[i]}'")
            if pattern[i] not in current_node.children:
                print(f"Character '{pattern[i]}' not found at current node.")
                return None
            child = current_node.children[pattern[i]]
            edge_length = child.edge_length(self.leaf_end)
            label = self.text[child.start: child.start + edge_length]
            print(f"Following edge labeled '{label}'")
            j = 0
            while j < len(label) and i < len(pattern):
                if pattern[i] != label[j]:
                    print(f"Mismatch: pattern character '{pattern[i]}' != edge label character '{label[j]}'")
                    return None
                i += 1
                j += 1
            current_node = child

        # Collect positions and word frequency from the subtree.
        positions = []
        word_frequency = 0

        def collect_positions(node):
            nonlocal word_frequency
            if node.index != -1:
                print(f"Leaf node reached at position(s): {node.positions} with word frequencies: {node.word_frequencies}")
                positions.extend(node.positions)
                word_frequency += node.word_frequencies.get(pattern, 0)
            for child in node.children.values():
                collect_positions(child)

        collect_positions(current_node)
        print(f"Collected positions (before boundary check): {positions}")

        # Validate positions based on word boundaries.
        valid_positions = []
        for pos in positions:
            if (pos == 0 or self.text[pos - 1] == '#') and \
            (pos + len(pattern) == len(self.text) or self.text[pos + len(pattern)] in ('#', '$')):
             valid_positions.append(pos)

        print(f"Valid positions after boundary check: {valid_positions}")


        if not valid_positions:
            print("No valid positions found after applying word boundary conditions.")
            return None

        return {
            "positions": valid_positions,
            "frequency": len(valid_positions)
        }


if __name__ == '__main__':
    filename = "suffix_tree.pkl"

    # Attempt to load an existing suffix tree.
    suffix_tree = SuffixTree.load_from_file(filename)

    # If not found, build the suffix tree using moby_words.
    if suffix_tree is None:
        words = load_moby_words()
        # Build a corpus where words are joined by '#' and terminated by '$'
        corpus_text = "#".join(word.lower() for word in words) + "$"
        suffix_tree = SuffixTree(corpus_text)
        suffix_tree.save_to_file(filename)

    # Interactive loop for word search.
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
