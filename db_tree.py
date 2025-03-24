# database_leaves.py
import sqlite3
import json

def setup_database(db_name="leaves.db"):
    """
    Create a single table 'leaves' with:
      id (PRIMARY KEY) -- unique leaf ID
      occurrences (TEXT) -- JSON { doc_name: [offsets], ... }
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY,
            occurrences TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn, cursor

def store_occurrences(cursor, occurrences_map):
    """
    occurrences_map = {
      leaf_id1: { "doc1.txt": [offsets...], "doc2.txt": [offsets...], ... },
      leaf_id2: { ... },
      ...
    }
    We store each leaf_id's doc→offsets dict as JSON in the 'leaves' table.
    """
    for leaf_id, doc_dict in occurrences_map.items():
        data_json = json.dumps(doc_dict)
        cursor.execute(
            "INSERT OR REPLACE INTO leaves (id, occurrences) VALUES (?, ?)",
            (leaf_id, data_json)
        )

def load_occurrences(cursor, leaf_id):
    """
    Retrieve doc->offsets JSON for a given leaf_id from 'leaves' table.
    Returns a dict or {} if not found.
    """
    cursor.execute("SELECT occurrences FROM leaves WHERE id = ?", (leaf_id,))
    row = cursor.fetchone()
    if row:
        return json.loads(row[0])
    return {}
