import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'kutuphane.db')

conn = sqlite3.connect(db_path)
c = conn.cursor()

# update all books to available
c.execute("UPDATE books SET is_available = 1")
conn.commit()

# also check if it worked
res = c.execute("SELECT count(*) FROM books WHERE is_available = 1").fetchone()
print(f"Update successful. {res[0]} books are now available.")

conn.close()
