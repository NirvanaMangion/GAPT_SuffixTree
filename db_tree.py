import sqlite3
import json
import csv

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

def export_to_csv(db_name="suffix_tree.db", csv_filename="database_copy.csv"):
    """Exports the contents of the database's leaves table to a CSV file."""
    conn, cursor = open_database(db_name)
    
    # Retrieve all rows from the 'leaves' table
    cursor.execute("SELECT id, occurrences FROM leaves")
    rows = cursor.fetchall()
    conn.close()
    
    # Check if there are rows to write
    if not rows:
        print(f"No data found in the '{db_name}' database.")
        return
    
    # Write the rows to a CSV file
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write the header row
        writer.writerow(["leaf_id", "occurrences"])
        
        # Write each database row
        for row in rows:
            leaf_id, occurrences_json = row
            # Parse occurrences JSON into a Python dictionary
            occurrences_dict = json.loads(occurrences_json)
            # You can choose to convert the dictionary to a string or process it differently
            occurrences_str = json.dumps(occurrences_dict)
            writer.writerow([leaf_id, occurrences_str])
    
    print(f"Exported {len(rows)} rows to {csv_filename}")

if __name__ == "__main__":
    # Example Usage:
    # If you'd like to create a database and insert some sample data:
    # (You may want to include this code or ensure it has been run before using export_to_csv)
    # create_database("suffix_tree.db")
    # store_occurrences(cursor, sample_data)  # Pass some sample data
    export_to_csv("suffix_tree.db", "database_copy.csv")
