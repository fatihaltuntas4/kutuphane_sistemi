from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
from database import get_db

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

@router.get("/most-borrowed")
def get_most_borrowed(db: Session = Depends(get_db)):
    result = db.query(
        models.Book.title, 
        func.count(models.BorrowTransaction.transaction_id).label("borrow_count")
    ).join(models.BorrowTransaction).group_by(models.Book.isbn).order_by(func.count(models.BorrowTransaction.transaction_id).desc()).limit(10).all()
    return [{"title": row.title, "borrow_count": row.borrow_count} for row in result]

@router.get("/active-users")
def get_active_users(db: Session = Depends(get_db)):
    result = db.query(
        models.User.email,
        func.count(models.BorrowTransaction.transaction_id).label("transaction_count")
    ).join(models.BorrowTransaction).group_by(models.User.user_id).order_by(func.count(models.BorrowTransaction.transaction_id).desc()).limit(10).all()
    return [{"email": row.email, "borrow_count": row.transaction_count} for row in result]

@router.get("/overdue")
def get_overdue_books(db: Session = Depends(get_db)):
    from datetime import date
    overdue_transactions = db.query(models.BorrowTransaction).filter(
        models.BorrowTransaction.return_date == None,
        models.BorrowTransaction.due_date < date.today()
    ).all()
    return [{"book_title": t.book.title, "user_email": t.user.email, "due_date": t.due_date} for t in overdue_transactions]

@router.get("/currently-borrowed")
def get_currently_borrowed(db: Session = Depends(get_db)):
    # Şu an ödünç alınmış kitaplar
    transactions = db.query(models.BorrowTransaction).filter(
        models.BorrowTransaction.status == models.StatusEnum.active
    ).all()
    return [{"book_title": t.book.title, "user_email": t.user.email, "borrow_date": t.borrow_date} for t in transactions]

@router.get("/monthly-stats")
def get_monthly_stats(db: Session = Depends(get_db)):
    # Aylık ödünç alma istatistikleri (PostgreSQL Uyumlu)
    result = db.query(
        func.to_char(models.BorrowTransaction.borrow_date, 'YYYY-MM').label('month'),
        func.count(models.BorrowTransaction.transaction_id).label('count')
    ).group_by('month').order_by('month').limit(12).all()
    return [{"month": row.month, "count": row.count} for row in result]
