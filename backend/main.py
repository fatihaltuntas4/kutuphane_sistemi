from fastapi import FastAPI
from database import engine, Base
import models
from routers import books, auth, transactions, reports

from fastapi.middleware.cors import CORSMiddleware

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kütüphane Yönetim Sistemi API", version="1.0")

# CORS ayarları (Frontend'in API'ye erişebilmesi için gerekli)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(transactions.router)
app.include_router(reports.router)

@app.get("/")
def read_root():
    return {"mesaj": "Kütüphane Yönetim Sistemi Backend API'sine Hoşgeldiniz!"}
