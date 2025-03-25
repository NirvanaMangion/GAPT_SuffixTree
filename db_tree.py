import sqlite3
import json

def create_database(db_name="suffix_tree.db"):
    """Creates an SQLite database with a table for storing suffix occurrences."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY,
            occurrences TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def store_occurrences(cursor, occurrences_map):
    """Stores occurrences (positions) of words in the database."""
    for leaf_id, doc_dict in occurrences_map.items():
        json_str = json.dumps(doc_dict)
        cursor.execute(
            "INSERT OR REPLACE INTO leaves (id, occurrences) VALUES (?, ?)",
            (leaf_id, json_str)
        )

def load_occurrences(cursor, leaf_id):
    """Loads occurrences from the database for a given leaf_id."""
    cursor.execute("SELECT occurrences FROM leaves WHERE id = ?", (leaf_id,))
    result = cursor.fetchone()
    return json.loads(result[0]) if result else {}

def open_database(db_name="suffix_tree.db"):
    """Opens a connection to the SQLite database and returns the connection and cursor."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    return conn, cursor
