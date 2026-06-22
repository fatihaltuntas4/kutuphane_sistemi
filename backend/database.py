import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Docker kullanılıyorsa çevresel değişkenden PostgreSQL URL'sini al, yoksa yerel SQLite kullan
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kutuphane.db')}"
)

# SQLite kullanılıyorsa özel bağlantı argümanları gerekir
connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency: API isteklerinde veritabanı oturumu almak için
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
