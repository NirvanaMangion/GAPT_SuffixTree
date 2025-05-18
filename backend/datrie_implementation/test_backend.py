# test_backend.py

import sys, os
print(f"→ ARGV: {sys.argv}")
print(f"→ CWD:   {os.getcwd()}")
print(f"→ FILE:  {__file__}")

import json
import sqlite3

from db_tree        import setup_database
from suffix_tree    import load_tree
from index_books    import index_books

print(f"→ Running test script: {__file__}")

def main():
    # 1) Ensure pages_map.json exists
    if not os.path.exists("pages_map.json"):
        raise RuntimeError("pages_map.json not found. Run main.py first.")

    # 2) Load pages_map.json
    with open("pages_map.json", "r", encoding="utf-8") as f:
        pages_map = json.load(f)

    print(f"✅ pages_map.json found with {len(pages_map)} books.")
    sample_book = next(iter(pages_map))
    num_pages    = len(pages_map[sample_book])
    print(f"   • Sample Book ID = {sample_book!r}, total pages = {num_pages}")

    # 3) Show the full text of page 1
    print("\n📄 — Page 1 Text —\n")
    print(pages_map[sample_book][0])  # entire first page
    print("\n" + ("─" * 40) + "\n")

    # 4) Re-index directly and compare counts
    trie, suffix_to_id = load_tree()
    if trie is None:
        raise RuntimeError("Suffix tree not built. Run main.py first.")

    conn, cursor = setup_database(":memory:")
    occ_map, pages_map_direct = index_books("Gutenberg_Books", suffix_to_id, cursor)
    print(f"✅ index_books() returned {len(pages_map_direct)} books too.")

    # 5) Compare page counts
    mismatches = []
    for book_id, pages in pages_map_direct.items():
        jid = str(book_id)
        if jid not in pages_map:
            mismatches.append(f"Book {jid!r} missing in pages_map.json")
        elif len(pages) != len(pages_map[jid]):
            mismatches.append(
                f"Book {jid!r}: pages.json={len(pages_map[jid])} vs index_books()={len(pages)}"
            )

    if mismatches:
        print("❌ MISMATCHES FOUND:")
        print("\n".join(mismatches))
    else:
        print("🎉 All page counts match. Backend paging is working correctly.")
    pass  # keep your real code here

if __name__ == "__main__":
    main()
    print("REACHED END OF SCRIPT")
