class SuffixTreeNode:
    def __init__(self):
        self.children = {}
        self.start = None
        self.end = None
        self.suffix_link = None

class SuffixTree:
    def __init__(self, text):
        self.text = text + "$"  # Append unique end character to ensure suffix uniqueness
        self.root = SuffixTreeNode()
        self.build_suffix_tree()

    def build_suffix_tree(self):
        for i in range(len(self.text)):
            self._add_suffix(i)

    def _add_suffix(self, suffix_start):
        node = self.root
        i = suffix_start

        while i < len(self.text):
            if self.text[i] not in node.children:
                new_node = SuffixTreeNode()
                new_node.start = i
                new_node.end = len(self.text)
                node.children[self.text[i]] = new_node
                return
            else:
                child = node.children[self.text[i]]
                j = child.start

                while j < child.end and i < len(self.text) and self.text[i] == self.text[j]:
                    i += 1
                    j += 1
                
                if j == child.end:
                    node = child  # Continue down the tree
                else:
                    split_node = SuffixTreeNode()
                    split_node.start = child.start
                    split_node.end = j
                    node.children[self.text[split_node.start]] = split_node
                    child.start = j
                    split_node.children[self.text[j]] = child
                    
                    new_leaf = SuffixTreeNode()
                    new_leaf.start = i
                    new_leaf.end = len(self.text)
                    split_node.children[self.text[i]] = new_leaf
                    return

    def search(self, pattern):
        node = self.root
        i = 0
        while i < len(pattern):
            if pattern[i] in node.children:
                child = node.children[pattern[i]]
                j = child.start
                while j < child.end and i < len(pattern) and self.text[j] == pattern[i]:
                    i += 1
                    j += 1
                if i == len(pattern):
                    return True  # Pattern found
                elif j == child.end:
                    node = child
                else:
                    return False  # Mismatch within the edge
            else:
                return False  # Character not found
        return True

    def print_tree(self, node=None, indent=""):
        if node is None:
            node = self.root
        for char, child in node.children.items():
            print(indent + self.text[child.start:child.end])
            self.print_tree(child, indent + "    ")

if __name__ == "__main__":
    sample_text = input("Enter the text to build the suffix tree: ")
    suffix_tree = SuffixTree(sample_text)
    suffix_tree.print_tree()
    
    while True:
        query = input("Enter a word to search (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        print(f"'{query}' found: {suffix_tree.search(query)}")
        