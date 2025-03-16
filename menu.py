import os
from book_download import main as download_books
from cleaned_tokenized import process_books
from my_suffix_tree import get_tokenized_books, build_suffix_trees, search_in_books

def main_menu():
    """
    Displays a main menu for the user to choose actions: download books, process books, or query books.
    """
    download_dir = "Gutenberg_Top_100"
    tokenized_books = None
    suffix_trees = None

    while True:
        print("\nMain Menu")
        print("1. Download Top 100 Books")
        print("2. Process and Tokenize Books")
        print("3. Query Books")
        print("4. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            download_books()
        elif choice == "2":
            tokenized_books = process_books(download_dir)
            suffix_trees = build_suffix_trees(tokenized_books)
            print("Processing complete.")
        elif choice == "3":
            if tokenized_books is None:
                tokenized_books = get_tokenized_books(download_dir)
                suffix_trees = build_suffix_trees(tokenized_books)
            
            while True:
                query = input("Enter a word to search (or type 'back' to return to the menu): ")
                if query.lower() == 'back':
                    break
                search_in_books(suffix_trees, tokenized_books, query)
        elif choice == "4":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main_menu()
