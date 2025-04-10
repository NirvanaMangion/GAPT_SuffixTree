import sqlite3
import csv

def export_leaves_to_csv(db_name="leaves.db", csv_filename="leaves.csv"):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Retrieve all rows from the 'leaves' table
    cursor.execute("SELECT id, occurrences FROM leaves")
    rows = cursor.fetchall()
    conn.close()
    
    # Write the rows to a CSV file
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write the header row
        writer.writerow(["leaf_id", "occurrences"])
        # Write each database row
        for row in rows:
            writer.writerow(row)
    
    print(f"Exported {len(rows)} rows to {csv_filename}")

if __name__ == "__main__":
    export_leaves_to_csv()
