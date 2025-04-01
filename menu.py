import os
import json
from suffix_tree import build_suffix_tree, save_tree, load_tree
from db_tree import create_database, store_occurrences, load_occurrences, open_database, export_to_csv
from main import load_word_list, index_books, search_word
from book_download import main as download_books  # Import book downloader

def menu():
    """Main interactive menu."""
    db_name = "suffix_tree.db"
    tree_file = "suffix_tree.pkl"
    folder = "Gutenberg_Top_100"

    create_database(db_name)
    conn, cursor = open_database(db_name)

    suffix_tree = None
    suffix_to_id = {}

    if os.path.exists(tree_file):
        suffix_tree, suffix_to_id = load_tree()
    else:
        print("Building suffix tree from words.txt...")
        word_list = load_word_list()
        suffix_tree, suffix_to_id = build_suffix_tree(word_list)
        save_tree(suffix_tree, suffix_to_id)
        print("Suffix tree built and saved.")

    while True:
        print("\n==== MENU ====")
        print("1. Download books from Project Gutenberg")
        print("2. Build suffix tree and index books")
        print("3. Search for a word")
        print("4. Export database to CSV")
        print("5. Exit")
        choice = input("Enter your choice (1–5): ").strip()

        if choice == "1":
            print("Starting book download...")
            download_books()

        elif choice == "2":
            print("Indexing books...")
            occurrences_map = index_books(folder, suffix_to_id)
            store_occurrences(cursor, occurrences_map)
            conn.commit()
            print("Indexing complete.")

        elif choice == "3":
            search_term = input("Enter a word to search: ").strip().lower()
            results = search_word(search_term, suffix_to_id, cursor)
            if results:
                print(f"\nOccurrences of '{search_term}':\n{json.dumps(results, indent=4)}")
            else:
                print(f"'{search_term}' not found.")

        elif choice == "4":
            export_to_csv(db_name)

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

    conn.close()

if __name__ == "__main__":
    menu()
