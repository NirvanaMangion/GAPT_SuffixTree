import sqlite3
import json
import csv
from suffix_pytrie import load_tree

DB_FILE = "suffix_tree.db"
CSV_FILE = "occurrences.csv"

def create_db():
    """
    Creates the SQLite database and the leaves table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY,
            occurrences TEXT
        )
    """)
    conn.commit()
    conn.close()

def store_occurrences(occurrences_map):
    """
    Stores the word occurrence positions in the database.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for leaf_id, doc_dict in occurrences_map.items():
        json_str = json.dumps(doc_dict)  # Convert occurrences to JSON
        cursor.execute(
            "INSERT OR REPLACE INTO leaves (id, occurrences) VALUES (?, ?)",
            (leaf_id, json_str)
        )

    conn.commit()
    conn.close()
    print(f"Stored {len(occurrences_map)} entries in the database.")

def fetch_occurrences(leaf_id):
    """
    Retrieves occurrences from the database by leaf_id.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT occurrences FROM leaves WHERE id = ?", (leaf_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])  # Convert JSON back to dictionary
    return {}

def is_database_populated():
    """
    Checks if the database already has indexed occurrences.
    Returns True if data exists, otherwise False.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leaves")
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0  # If count > 0, data already exists

def export_to_csv():
    """
    Exports the database to a CSV file for easier readability.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leaves")

    rows = cursor.fetchall()
    conn.close()

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Occurrences"])  # CSV Headers

        for row in rows:
            writer.writerow(row)

    print(f"Database exported to {CSV_FILE} successfully!")

def search_word(word, suffix_to_id):
    """
    Searches for a word's occurrences in indexed books.
    """
    word = word.strip().lower()
    leaf_id = suffix_to_id.get(word)

    if not leaf_id:
        print(f"'{word}' not found in the suffix tree.")
        return

    # Fetch occurrences from database
    occurrences = fetch_occurrences(leaf_id)

    if not occurrences:
        print(f"No occurrences found for '{word}'.")
        return

    print(f"'{word}' found in:")
    for filename, positions in occurrences.items():
        print(f"- {filename}: {len(positions)} occurrences at positions {positions[:5]}...")
