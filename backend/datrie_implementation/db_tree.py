import sqlite3
import json

def setup_database(db_name="leaves.db"):
    conn = sqlite3.connect(db_name)     # Connect to SQLite DB (or create it)
    cursor = conn.cursor()

    # Create the 'mapping' table for suffix-tree leaf occurrences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mapping (
            leaf_id INTEGER PRIMARY KEY,
            data TEXT NOT NULL
        )
    ''')

    # Create the 'books' table to map book names to unique IDs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    conn.commit()  # Save table creation
    return conn, cursor  # Return DB connection and cursor


def get_or_create_book_id(cursor, book_name):
    cursor.execute("SELECT id FROM books WHERE name = ?", (book_name,))
    row = cursor.fetchone()
    if row:
        return row[0]  # Return existing book ID
    else:
        cursor.execute("INSERT INTO books (name) VALUES (?)", (book_name,))
        return cursor.lastrowid  # Return new ID after insert



def store_occurrences(cursor, occurrences_map):
    # Convert the nested dictionary to JSON for DB storage
    data = [(leaf_id, json.dumps(book_offsets)) for leaf_id, book_offsets in occurrences_map.items()]
    cursor.executemany(
        "INSERT OR REPLACE INTO mapping (leaf_id, data) VALUES (?, ?)",
        data
    )


def load_occurrences(cursor, leaf_id):
    cursor.execute("SELECT data FROM mapping WHERE leaf_id = ?", (leaf_id,))
    row = cursor.fetchone()
    if row:
        return json.loads(row[0])  # Parse JSON back into Python dict
    return {}  # Return empty dict if no match
