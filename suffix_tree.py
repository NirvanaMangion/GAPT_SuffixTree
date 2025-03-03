class SuffixTreeNode:
    def __init__(self, start, end):
        self.children = {}  # Maps characters to child nodes.
        self.suffix_link = None
        self.start = start
        self.end = end  # For leaves, end is a reference (list) to the global end.
        self.index = -1  # For leaf nodes, this can store the starting index of the suffix.

    def edge_length(self, current_position):
        """
        Returns the length of the edge from this node.
        If this is a leaf, self.end is a pointer (list) whose first element is the current end.
        """
        if isinstance(self.end, list):
            return self.end[0] - self.start + 1
        else:
            return self.end - self.start + 1


class SuffixTree:
    def __init__(self, text):
        self.text = text
        self.size = len(text)
        # Create root node. For the root, start and end are set to -1.
        self.root = SuffixTreeNode(-1, -1)
        self.root.suffix_link = self.root

        # Active point variables.
        self.active_node = self.root
        self.active_edge = -1
        self.active_length = 0

        # The number of suffixes yet to be added.
        self.remaining_suffix_count = 0

        # Global end for all leaves. We use a list to simulate a pointer.
        self.leaf_end = [-1]

        # The last internal node created in the current phase (for suffix link updates).
        self.last_new_node = None

        # Build the tree by iterating over the input string.
        self.build_tree()
        # (Optional) Set suffix indices on leaves via DFS.
        self.set_suffix_index_by_dfs(self.root, 0)

    def build_tree(self):
        for pos in range(self.size):
            self.extend_suffix_tree(pos)

    def extend_suffix_tree(self, pos):
        """
        This method extends the tree by the character at position pos.
        It updates the active point and uses suffix links to ensure linear time complexity.
        """
        # Update the global leaf end.
        self.leaf_end[0] = pos
        self.remaining_suffix_count += 1
        self.last_new_node = None

        while self.remaining_suffix_count > 0:
            if self.active_length == 0:
                self.active_edge = pos

            current_char = self.text[self.active_edge]
            # If there is no edge starting with the current active edge character,
            # create a new leaf (Rule 2).
            if current_char not in self.active_node.children:
                self.active_node.children[current_char] = SuffixTreeNode(pos, self.leaf_end)
                # If an internal node was waiting for a suffix link, set it now.
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

                # If the next character on the edge is the same as the current character,
                # no new node is needed (Rule 3) – just increment the active_length.
                if self.text[next_node.start + self.active_length] == self.text[pos]:
                    if self.last_new_node is not None and self.active_node != self.root:
                        self.last_new_node.suffix_link = self.active_node
                        self.last_new_node = None
                    self.active_length += 1
                    break

                # Otherwise, we need to split the edge (Rule 2).
                split_end = next_node.start + self.active_length - 1
                split_node = SuffixTreeNode(next_node.start, split_end)
                self.active_node.children[current_char] = split_node
                # Create a new leaf for the current character.
                split_node.children[self.text[pos]] = SuffixTreeNode(pos, self.leaf_end)
                # Adjust the next_node to start after the split.
                next_node.start += self.active_length
                split_node.children[self.text[next_node.start]] = next_node

                # If an internal node was waiting for a suffix link, point it to split_node.
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
        """
        A depth-first traversal to set the index of each leaf node.
        The index is the starting position of the suffix in the text.
        """
        if not node:
            return
        if len(node.children) == 0:
            node.index = self.size - label_height
            return
        for child in node.children.values():
            self.set_suffix_index_by_dfs(child, label_height + child.edge_length(self.leaf_end[0]))

    def print_tree(self, node=None, indent=""):
        """
        A helper method to print the suffix tree.
        Each edge is printed by showing its corresponding substring.
        """
        if node is None:
            node = self.root
        for child in node.children.values():
            edge_length = child.edge_length(self.leaf_end[0])
            label = self.text[child.start: child.start + edge_length]
            print(indent + label)
            self.print_tree(child, indent + "  ")

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


def load_words_from_file(path):
    """
    Loads words from a text file where words are cleaned and separated by spaces.
    Returns a single string that joins the words with a delimiter (here '#') that is not present in the words.
    """
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    words = content.split()  # Split on whitespace.
    return "#".join(words)


if __name__ == '__main__':
    # Provide the path to your file. The file is assumed to have words separated by spaces.
    file_path = "Gutenberg_Top_100/Les Misérables by Victor Hugo (442).txt"
    corpus_text = load_words_from_file(file_path)

    # Append a unique termination symbol if not already present.
    if not corpus_text.endswith("$"):
        corpus_text += "$"

    # Build the suffix tree using Ukkonen's algorithm.
    st = SuffixTree(corpus_text)
    print("Suffix Tree:")
    # Sample search queries.
    search_terms = ["apple", "tion", "xyz", "the", "ing", "miserables"]
    print("\nSearch Results:")
    for term in search_terms:
        result = st.search(term)
        print(f"Does '{term}' exist in the dataset? {result}")
