import csv
import os
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models

# Yollar
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS_CSV = os.path.join(BASE_DIR, "books_data", "books.csv")
USERS_CSV = os.path.join(BASE_DIR, "books_data", "users.csv")

def import_data(book_limit=2000, user_limit=50):
    db = SessionLocal()
    
    # 1. KİTAPLARI EKLE (books.csv)
    if os.path.exists(BOOKS_CSV):
        print("Kitaplar içeri aktarılıyor...")
        count = 0
        try:
            with open(BOOKS_CSV, mode='r', encoding='latin-1') as file:
                reader = csv.DictReader(file, delimiter=';', escapechar='\\')
                for row in reader:
                    isbn = row.get("ISBN", "").strip()
                    title = row.get("Book-Title", "").strip()
                    author = row.get("Book-Author", "").strip()
                    publisher = row.get("Publisher", "").strip()
                    year_str = row.get("Year-Of-Publication", "0").strip()
                    
                    try:
                        year = int(year_str)
                    except ValueError:
                        year = 0
                        
                    if not isbn or not title:
                        continue
                        
                    # Veritabanında varsa atla
                    existing_book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
                    if not existing_book:
                        book = models.Book(
                            isbn=isbn,
                            title=title,
                            author=author,
                            publisher=publisher,
                            publication_year=year,
                            is_available=True
                        )
                        db.add(book)
                        count += 1
                        
                        if count % 100 == 0:
                            db.commit()
                            print(f"{count} kitap eklendi...")
                            
                        if book_limit and count >= book_limit:
                            break
                db.commit()
                print(f"Toplam {count} kitap başarıyla aktarıldı.")
        except Exception as e:
            print("Kitap yükleme hatası:", e)
            db.rollback()

    # 2. KULLANICILARI EKLE (users.csv)
    if os.path.exists(USERS_CSV):
        print("Kullanıcılar içeri aktarılıyor...")
        count = 0
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_pwd = pwd_context.hash("123456") # Varsayılan şifre

        try:
            with open(USERS_CSV, mode='r', encoding='latin-1') as file:
                reader = csv.DictReader(file, delimiter=';', escapechar='\\')
                for row in reader:
                    user_id_str = row.get("User-ID", "").strip()
                    location = row.get("Location", "").strip()
                    
                    if not user_id_str:
                        continue
                    
                    email = f"user{user_id_str}@kutuphane.com"
                    
                    existing_user = db.query(models.User).filter(models.User.email == email).first()
                    if not existing_user:
                        user = models.User(
                            full_name=f"Kaggle User {user_id_str} ({location.split(',')[0]})",
                            email=email,
                            hashed_password=hashed_pwd,
                            role=models.RoleEnum.student
                        )
                        db.add(user)
                        count += 1
                        
                        if count % 50 == 0:
                            db.commit()
                            print(f"{count} kullanıcı eklendi...")
                            
                        if user_limit and count >= user_limit:
                            break
                db.commit()
                print(f"Toplam {count} kullanıcı başarıyla aktarıldı.")
        except Exception as e:
            print("Kullanıcı yükleme hatası:", e)
            db.rollback()

    db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    import_data(book_limit=2000, user_limit=50)
