
import sqlite3
from core import Config

def GenerateDBStructure():
    conn = sqlite3.connect("OSINT.db")

    conn.execute("""CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY ASC,
                details TEXT DEFAULT '',
                start_vector_type TEXT NOT NULL
    );""")

    def GenParams(v):
        for c in Config.GetConfig()['vector_types'][v]:
            if c.startswith('%'):
                pass
            else:
                yield f"{c} TEXT NOT NULL,\n"

    for v in Config.GetConfig()['vector_types']:
        conn.execute(f"""CREATE TABLE IF NOT EXISTS {v + 's'} (
                    {''.join(GenParams(v))}
                    id INTEGER PRIMARY KEY ASC,
                    target_id INT NOT NULL,
                    is_starting_vector BOOLEAN DEFAULT FALSE
        );""")

    conn.commit()
    conn.close()