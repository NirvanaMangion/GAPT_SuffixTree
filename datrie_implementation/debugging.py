from moby_words import load_moby_words

words = load_moby_words()
print(f"Total words loaded: {len(words)}")
unique_words = set(words)
print(f"Unique words: {len(unique_words)}")

