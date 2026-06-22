from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from database import Base

class RoleEnum(enum.Enum):
    admin = "Yönetici"
    librarian = "Kütüphaneci"
    student = "Öğrenci"

class StatusEnum(enum.Enum):
    active = "Aktif"
    returned = "İade Edildi"
    overdue = "Gecikti"

class ReservationStatusEnum(enum.Enum):
    pending = "Bekliyor"
    completed = "Tamamlandı"
    cancelled = "İptal Edildi"

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.student)

    # İlişkiler
    borrowings = relationship("BorrowTransaction", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")

class Book(Base):
    __tablename__ = "books"

    isbn = Column(String, primary_key=True, index=True) # Kaggle datasetindeki ISBN anahtar olacak
    title = Column(String, index=True)
    author = Column(String, index=True)
    publisher = Column(String)
    publication_year = Column(Integer)
    is_available = Column(Boolean, default=True) # Kitap ödünç alınabilir mi?

    # İlişkiler
    borrowings = relationship("BorrowTransaction", back_populates="book")
    reservations = relationship("Reservation", back_populates="book")

class BorrowTransaction(Base):
    __tablename__ = "borrow_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    isbn = Column(String, ForeignKey("books.isbn"))
    borrow_date = Column(Date)
    due_date = Column(Date)
    return_date = Column(Date, nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.active)

    user = relationship("User", back_populates="borrowings")
    book = relationship("Book", back_populates="borrowings")

class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    isbn = Column(String, ForeignKey("books.isbn"))
    reservation_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(ReservationStatusEnum), default=ReservationStatusEnum.pending)

    user = relationship("User", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")
