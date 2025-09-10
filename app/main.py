from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import schemas, models
from .core.database import engine, get_db

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
    
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book