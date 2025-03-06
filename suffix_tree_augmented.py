def augment_suffix_tree(suffix_tree, text):
    """
    Enhances the suffix tree nodes with additional metadata such as word offsets and frequencies.
    """
    print("Augmenting suffix tree with word offsets and frequencies...")

    def dfs(node, depth=0):
        """
        Traverse the tree in a depth-first manner and add metadata.
        """
        if not node.children:
            word = text[node.start: node.end[0] + 1]

            # Ensure attributes exist
            if not hasattr(node, "positions"):
                node.positions = []
            if not hasattr(node, "word_frequencies"):
                node.word_frequencies = {}

            # Store the position of this suffix
            node.positions.append(node.start)

            # Update frequency count
            if word in node.word_frequencies:
                node.word_frequencies[word] += 1
            else:
                node.word_frequencies[word] = 1

            # **Debugging print statements**
            print(f"Processed word: '{word}', Position: {node.start}, Frequency: {node.word_frequencies[word]}")

        for child in node.children.values():
            dfs(child, depth + 1)

    # **Confirm that DFS is actually running**
    print("Starting depth-first traversal of the suffix tree...")
    dfs(suffix_tree.root)
    print("Suffix tree augmentation complete.")
