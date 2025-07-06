import sqlite3

def GetDBConnection():
    conn = sqlite3.connect("OSINT.db")
    cursor = conn.cursor()

    return conn,cursor


def EndDBConnection(conn,cursor):
    conn.commit()
    cursor.close()
    conn.close()