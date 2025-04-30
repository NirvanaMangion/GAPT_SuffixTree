import re

def search_sentences(query, sentence_map, use_regex=False):
    """
    Search indexed sentences for a phrase or regex pattern.
    """
    if use_regex:
        try:
            pattern = re.compile(query, re.IGNORECASE)
        except re.error as e:
            print(f"Invalid regex: {e}")
            return
    else:
        pattern = query.lower()

    match_count = 0
    print(f"\n🔍 Searching for: {'regex' if use_regex else 'phrase'} → {query}\n")

    for book, sentences in sentence_map.items():
        for idx, sentence in enumerate(sentences):
            text = sentence.strip()
            if use_regex:
                if pattern.search(text):
                    print(f"📘 {book} [#{idx}]: {text}")
                    match_count += 1
            else:
                if pattern in text.lower():
                    print(f"📘 {book} [#{idx}]: {text}")
                    match_count += 1

    print(f"\n Matches found: {match_count}")
