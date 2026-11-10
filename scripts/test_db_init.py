import sys
import os
import sqlite3

sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import init_db, engine, Base
import app.models

def main():
    print("Initializing database tables...")
    init_db()
    
    # Verify tables in SQLite
    con = sqlite3.connect("career_intelligence.db")
    cur = con.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    con.close()
    
    print(f"Total tables created in career_intelligence.db: {len(tables)}")
    for t in sorted(tables):
        print(f" - {t}")

if __name__ == "__main__":
    main()
