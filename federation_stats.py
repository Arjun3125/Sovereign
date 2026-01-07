# federation_stats.py
# Display doctrine federation statistics

import os
import sqlite3
from pathlib import Path
from doctrine_federation import DoctrineFederation

def main():
    workspace = Path("workspace")
    dbs = {}
    
    for dirpath, _, filenames in os.walk(workspace):
        for f in filenames:
            if f == "doctrine_vectors.db":
                db = os.path.join(dirpath, f)
                book_name = Path(dirpath).parent.name
                dbs[book_name] = db
    
    if not dbs:
        print("No doctrine DBs found.")
        return
    
    fed = DoctrineFederation(dbs)
    fed.stats()

if __name__ == "__main__":
    main()
