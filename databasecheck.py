import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "event.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("USERS TABLE:")
for row in cursor.execute("SELECT * FROM users"):
    print(row)

print("\nEVENTS TABLE:")
for row in cursor.execute("SELECT * FROM events"):
    print(row)

print("\nPARTICIPANTS TABLE:")
for row in cursor.execute("SELECT * FROM participants"):
    print(row)

conn.close()
