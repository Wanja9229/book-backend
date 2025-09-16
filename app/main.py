from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import schemas, models
from .core.database import engine, get_db
from .core.config import settings  # 설정 import 추가
import cloudinary.uploader
from typing import List

app = FastAPI()

@app.get("/")
def read_root():
    return {"message":"Book Api is running"}

@app.post("/books/", response_model=schemas.Book)
def create_books(book:schemas.BookCreate, db: Session = Depends(get_db)):
    # ISBN 중복 체크
    db_book = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if db_book:
        raise HTTPException(status_code=400, detail="ISBN already registered")
    
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get('/books/', response_model=List[schemas.Book])
def get_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = db.query(models.Book).order_by(models.Book.created_at.desc()).offset(skip).limit(limit).all()
    return books

@app.get('/books/{book_id}', response_model=schemas.Book)
def get_book_by_id(book_id:int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put("/books/{book_id}", response_model=schemas.Book)  # PUT 사용
def update_book_full(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # 전체 필드 업데이트
    for field, value in book.model_dump().items():
        setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/{book_id}/edit", response_model=schemas.Book)
def get_book_for_edit(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    # 책 존재 확인
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # 삭제
    db.delete(db_book)
    db.commit()
    return {"message": f"Book {book_id} deleted successfully"}