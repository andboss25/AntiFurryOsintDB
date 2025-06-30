
import sqlite3

def GenerateDBStructure():
    conn = sqlite3.connect("OSINT.db")

    conn.execute("""CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY ASC,
                details TEXT DEFAULT '',
                start_vector_type TEXT NOT NULL
    );""")

    conn.execute("""CREATE TABLE IF NOT EXISTS usernames (
                id INTEGER PRIMARY KEY ASC,
                username TEXT NOT NULL,
                platform TEXT NOT NULL,
                target_id INT NOT NULL,
                is_starting_vector BOOLEAN DEFAULT FALSE
    );""")

    conn.commit()
    conn.close()