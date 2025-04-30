# database_leaves.py
import sqlite3
import json

def setup_database(db_name="leaves.db"):
    """
    Create two tables:
      1. mapping:
         - leaf_id: INTEGER PRIMARY KEY
         - data: TEXT NOT NULL, storing a JSON blob with occurrences
           where keys are numeric book IDs and values are lists of offsets.
      2. books:
         - id: INTEGER PRIMARY KEY AUTOINCREMENT,
         - name: TEXT NOT NULL
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create the mapping table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mapping (
            leaf_id INTEGER PRIMARY KEY,
            data TEXT NOT NULL
        )
    ''')
    # Create the books table with a numeric primary key and book name.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn, cursor

def get_or_create_book_id(cursor, book_name):
    """
    Retrieve the numeric book ID for the given book_name from the books table.
    If the book does not exist, insert it and return the new ID.
    """
    cursor.execute("SELECT id FROM books WHERE name = ?", (book_name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute("INSERT INTO books (name) VALUES (?)", (book_name,))
        return cursor.lastrowid

def store_occurrences(cursor, occurrences_map):
    """
    Given an occurrences_map of the form:
      { leaf_id: { book_id: [offsets...], ... }, ... }
    Convert each inner dictionary to a JSON string and insert into mapping.
    """
    data = [(leaf_id, json.dumps(book_offsets)) for leaf_id, book_offsets in occurrences_map.items()]
    cursor.executemany(
        "INSERT OR REPLACE INTO mapping (leaf_id, data) VALUES (?, ?)",
        data
    )

def load_occurrences(cursor, leaf_id):
    """
    Retrieve the JSON blob for a given leaf_id from the 'mapping' table.
    Returns a dictionary mapping numeric book IDs to lists of offsets, or {} if not found.
    """
    cursor.execute("SELECT data FROM mapping WHERE leaf_id = ?", (leaf_id,))
    row = cursor.fetchone()
    if row:
        return json.loads(row[0])
    return {}
