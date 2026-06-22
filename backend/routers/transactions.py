from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import models
from database import get_db
from pydantic import BaseModel

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

class BorrowRequest(BaseModel):
    email: str
    isbn: str
    days: int = 15

class ReturnRequest(BaseModel):
    transaction_id: int

class ReservationRequest(BaseModel):
    email: str
    isbn: str

@router.post("/borrow")
def borrow_book(request: BorrowRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
    book = db.query(models.Book).filter(models.Book.isbn == request.isbn).first()
    if not book:
        raise HTTPException(status_code=404, detail="Kitap bulunamadı")
    if not book.is_available:
        raise HTTPException(status_code=400, detail="Kitap şu anda başkası tarafından ödünç alınmış. Lütfen rezervasyon yapın.")
    
    borrow_date = date.today()
    due_date = borrow_date + timedelta(days=request.days)
    
    new_transaction = models.BorrowTransaction(
        user_id=user.user_id,
        isbn=book.isbn,
        borrow_date=borrow_date,
        due_date=due_date,
        status=models.StatusEnum.active
    )
    
    book.is_available = False
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return {"mesaj": "Kitap başarıyla ödünç alındı", "islem_id": new_transaction.transaction_id}

@router.post("/return")
def return_book(request: ReturnRequest, db: Session = Depends(get_db)):
    transaction = db.query(models.BorrowTransaction).filter(models.BorrowTransaction.transaction_id == request.transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="İşlem bulunamadı")
    if transaction.status == models.StatusEnum.returned:
        raise HTTPException(status_code=400, detail="Bu kitap zaten iade edilmiş")
        
    book = db.query(models.Book).filter(models.Book.isbn == transaction.isbn).first()
    
    transaction.return_date = date.today()
    if transaction.return_date > transaction.due_date:
        transaction.status = models.StatusEnum.overdue
    else:
        transaction.status = models.StatusEnum.returned
        
    book.is_available = True
    db.commit()
    
    return {"mesaj": "Kitap başarıyla iade edildi"}

@router.post("/reserve")
def reserve_book(request: ReservationRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    book = db.query(models.Book).filter(models.Book.isbn == request.isbn).first()
    if not book:
        raise HTTPException(status_code=404, detail="Kitap bulunamadı")
    if book.is_available:
        raise HTTPException(status_code=400, detail="Kitap zaten kütüphanede mevcut, direkt ödünç alabilirsiniz.")
        
    existing = db.query(models.Reservation).filter(
        models.Reservation.user_id == user.user_id,
        models.Reservation.isbn == request.isbn,
        models.Reservation.status == models.ReservationStatusEnum.pending
    ).first()
    
    if existing:
         raise HTTPException(status_code=400, detail="Zaten bu kitap için bekleyen bir rezervasyonunuz var.")
         
    new_reservation = models.Reservation(
        user_id=user.user_id,
        isbn=request.isbn
    )
    db.add(new_reservation)
    db.commit()
    
    return {"mesaj": "Rezervasyon oluşturuldu."}

@router.get("/me")
def get_my_transactions(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
    transactions = db.query(models.BorrowTransaction).filter(models.BorrowTransaction.user_id == user.user_id).order_by(models.BorrowTransaction.borrow_date.desc()).all()
    
    results = []
    for t in transactions:
        results.append({
            "transaction_id": t.transaction_id,
            "book_title": t.book.title,
            "borrow_date": t.borrow_date,
            "due_date": t.due_date,
            "status": t.status.value
        })
    return results

@router.get("/reservations/me")
def get_my_reservations(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
    reservations = db.query(models.Reservation).filter(models.Reservation.user_id == user.user_id).all()
    
    results = []
    for r in reservations:
        results.append({
            "reservation_id": r.reservation_id,
            "book_title": r.book.title,
            "reservation_date": r.reservation_date,
            "status": r.status.value
        })
    return results

@router.delete("/reserve/{reservation_id}")
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
    res = db.query(models.Reservation).filter(models.Reservation.reservation_id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı")
    if res.status != models.ReservationStatusEnum.pending:
        raise HTTPException(status_code=400, detail="Sadece bekleyen rezervasyonlar iptal edilebilir")
    
    res.status = models.ReservationStatusEnum.cancelled
    db.commit()
    return {"mesaj": "Rezervasyon iptal edildi."}

@router.get("/all")
def get_all_transactions(db: Session = Depends(get_db)):
    # Yöneticiler için tüm işlemleri getir
    transactions = db.query(models.BorrowTransaction).order_by(models.BorrowTransaction.borrow_date.desc()).limit(100).all()
    results = []
    for t in transactions:
        results.append({
            "transaction_id": t.transaction_id,
            "user_email": t.user.email,
            "book_title": t.book.title,
            "borrow_date": t.borrow_date,
            "due_date": t.due_date,
            "status": t.status.value
        })
    return results
