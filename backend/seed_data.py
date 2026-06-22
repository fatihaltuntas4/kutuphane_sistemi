from .database import SessionLocal, engine, Base
from .models import Book

def load_mock_books():
    # Geçici mock veri seti oluşturuyoruz
    mock_data = [
        {"isbn": "978-0131103627", "title": "The C Programming Language", "author": "Brian W. Kernighan", "publisher": "Prentice Hall", "publication_year": 1988},
        {"isbn": "978-0201616224", "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "publisher": "Addison-Wesley", "publication_year": 1999},
        {"isbn": "978-0596009205", "title": "Head First Java", "author": "Kathy Sierra", "publisher": "O'Reilly", "publication_year": 2005},
        {"isbn": "978-1449331818", "title": "Learning Python", "author": "Mark Lutz", "publisher": "O'Reilly", "publication_year": 2013}
    ]
    
    db = SessionLocal()
    try:
        for data in mock_data:
            book = Book(**data)
            db.merge(book) # merge kullanarak eğer aynı isbn varsa hata vermemesini sağlıyoruz
        db.commit()
        print("Mock veriler başarıyla veritabanına eklendi.")
    except Exception as e:
        print(f"Veri ekleme sırasında bir hata oluştu: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    load_mock_books()
