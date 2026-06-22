from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import models
from database import get_db
from pydantic import BaseModel

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)

class BookBase(BaseModel):
    title: str
    author: str
    publisher: str
    publication_year: int
    is_available: bool = True

class BookCreate(BookBase):
    isbn: str

class BookResponse(BookBase):
    isbn: str
    class Config:
        orm_mode = True

@router.get("/", response_model=List[BookResponse])
def get_books(q: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.Book)
    if q:
        search = f"%{q}%"
        query = query.filter(models.Book.title.ilike(search) | models.Book.author.ilike(search) | models.Book.isbn.ilike(search))
    return query.offset(skip).limit(limit).all()

@router.get("/{isbn}", response_model=BookResponse)
def get_book_by_isbn(isbn: str, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if not book:
        raise HTTPException(status_code=404, detail="Kitap bulunamadı")
    return book

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if db_book:
        raise HTTPException(status_code=400, detail="Bu ISBN ile kayıtlı bir kitap zaten var")
    
    new_book = models.Book(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@router.delete("/{isbn}")
def delete_book(isbn: str, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if not book:
        raise HTTPException(status_code=404, detail="Kitap bulunamadı")
    
    # Kitaba bağlı aktif işlem var mı kontrol et (basitçe)
    active_borrows = db.query(models.BorrowTransaction).filter(
        models.BorrowTransaction.isbn == isbn,
        models.BorrowTransaction.status == models.StatusEnum.active
    ).first()
    
    if active_borrows:
        raise HTTPException(status_code=400, detail="Bu kitap şu an ödünç alınmış, silinemez.")
        
    db.delete(book)
    db.commit()
    return {"mesaj": "Kitap başarıyla silindi"}
