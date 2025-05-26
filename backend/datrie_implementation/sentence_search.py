import re

# Search sentences using a regex or plain phrase
def search_sentences(query, sentence_map, use_regex=False):
    if use_regex:
        try:
            pattern = re.compile(query, re.IGNORECASE)  # compile regex pattern
        except re.error as e:
            print(f"Invalid regex: {e}")
            return
    else:
        pattern = query.lower()  # normalize plain text query

    match_count = 0
    print(f"\n🔍 Searching for: {'regex' if use_regex else 'phrase'} → {query}\n")

    for book, sentences in sentence_map.items():
        for idx, sentence in enumerate(sentences):
            text = sentence.strip()  # remove leading/trailing spaces
            if use_regex:
                text_clean = re.sub(r'[\.!?]+$', '', text)  # remove end punctuation
                if pattern.search(text_clean):  # regex match
                    print(f"📘 {book} [#{idx}]: {text}")
                    match_count += 1
            else:
                if pattern in text.lower():  # substring match
                    print(f"📘 {book} [#{idx}]: {text}")
                    match_count += 1

    print(f"\n Matches found: {match_count}")
