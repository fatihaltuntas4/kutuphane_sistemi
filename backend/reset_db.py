import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'kutuphane.db')

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Tüm kitapları tekrar müsait yap
c.execute("UPDATE books SET is_available = 1")

# Önceki hatalı veya test amaçlı yapılmış tüm ödünç alma ve rezervasyonları sil
c.execute("DELETE FROM borrow_transactions")
c.execute("DELETE FROM reservations")

conn.commit()
conn.close()

print("Veritabanı sıfırlandı: Tüm kitaplar müsait, tüm işlemler temizlendi.")
