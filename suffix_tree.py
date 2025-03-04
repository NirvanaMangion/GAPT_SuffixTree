from moby_words import load_moby_words

class SuffixTreeNode:
    def __init__(self, start, end):
        self.children = {}  # Maps characters to child nodes.
        self.suffix_link = None
        self.start = start
        self.end = end  # For leaves, end is a reference (list) to the global end.
        self.index = -1  # For leaf nodes, this can store the starting index of the suffix.

    def edge_length(self, current_position):
        if isinstance(self.end, list):
            return self.end[0] - self.start + 1
        else:
            return self.end - self.start + 1


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
        self.leaf_end = [-1]
        self.last_new_node = None

        self.build_tree()
        self.set_suffix_index_by_dfs(self.root, 0)

    def build_tree(self):
        for pos in range(self.size):
            self.extend_suffix_tree(pos)

    def extend_suffix_tree(self, pos):
        self.leaf_end[0] = pos
        self.remaining_suffix_count += 1
        self.last_new_node = None

        while self.remaining_suffix_count > 0:
            if self.active_length == 0:
                self.active_edge = pos

            current_char = self.text[self.active_edge]
            if current_char not in self.active_node.children:
                self.active_node.children[current_char] = SuffixTreeNode(pos, self.leaf_end)
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

                split_node.children[self.text[pos]] = SuffixTreeNode(pos, self.leaf_end)
                next_node.start += self.active_length
                split_node.children[self.text[next_node.start]] = next_node

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
            self.set_suffix_index_by_dfs(child, label_height + child.edge_length(self.leaf_end[0]))

    def search(self, pattern):
        """
        Searches for the given pattern in the suffix tree.
        Returns True if the pattern exists, False otherwise.
        """
        current_node = self.root
        i = 0
        while i < len(pattern):
            if pattern[i] in current_node.children:
                child = current_node.children[pattern[i]]
                edge_length = child.edge_length(self.leaf_end[0])
                label = self.text[child.start: child.start + edge_length]
                j = 0
                while j < len(label) and i < len(pattern):
                    if pattern[i] != label[j]:
                        return False
                    i += 1
                    j += 1
                current_node = child
            else:
                return False
        return True


if __name__ == '__main__':
    print("Loading Moby Words dataset into Suffix Tree...")

    # Load Moby Words dataset (downloads if not available)
    words = load_moby_words()

    # Convert words into a single string with a delimiter
    corpus_text = "#".join(words) + "$"

    # Build the suffix tree
    suffix_tree = SuffixTree(corpus_text)

    print("Suffix Tree built successfully with Moby Words dataset.")

    # Test search functionality
    search_terms = ["apple", "banana", "universe", "guitar", "programming", "xyz"]
    print("\nSearch Results:")
    for term in search_terms:
        result = suffix_tree.search(term)
        print(f"Does '{term}' exist in the dataset? {result}")
