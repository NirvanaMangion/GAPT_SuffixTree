import sqlite3
import csv
import os

def create_database(db_name="suffix_tree.db"):
    """Creates a SQLite database and a table for storing leaf occurrences."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            leaf_id INTEGER,
            filename TEXT,
            position INTEGER
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leaf_id ON leaves(leaf_id)")
    conn.commit()
    conn.close()

def open_database(db_name="suffix_tree.db"):
    """Opens a connection to the database and returns connection and cursor."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    return conn, cursor

def store_occurrences(cursor, occurrences_map):
    """Stores all leaf occurrences in the database using batch insert."""
    data_to_insert = [
        (leaf_id, filename, position)
        for leaf_id, file_map in occurrences_map.items()
        for filename, positions in file_map.items()
        for position in positions
    ]

    cursor.executemany(
        "INSERT INTO leaves (leaf_id, filename, position) VALUES (?, ?, ?)",
        data_to_insert
    )

def load_occurrences(cursor, leaf_id):
    """Retrieves all positions of a given leaf ID from the database."""
    cursor.execute("SELECT filename, position FROM leaves WHERE leaf_id = ?", (leaf_id,))
    rows = cursor.fetchall()

    occurrences = {}
    for filename, position in rows:
        occurrences.setdefault(filename, []).append(position)

    return occurrences

def export_to_csv(db_name="suffix_tree.db", output_file="suffix_tree_data.csv"):
    """Exports the database contents to a CSV file."""
    if not os.path.exists(db_name):
        print(f"Database {db_name} not found.")
        return

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT leaf_id, filename, position FROM leaves")

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["leaf_id", "filename", "position"])
        writer.writerows(cursor.fetchall())

    conn.close()
    print(f"Exported data to {output_file}")
