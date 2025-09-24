from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from . import schemas
from .models import Book, Board, Post  # Board 오타 수정, Post 추가
from datetime import date
from .core.database import engine, get_db, Base
from .core.config import settings  # 이미 Cloudinary 초기화 완료
import cloudinary.uploader  # 직접 import
from typing import List, Optional

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message":"Book Api is running"}


def create_initial_data():
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 기본 게시판이 없으면 생성
    if not db.query(Board).first():
        boards = [
            Board(name="공지사항", slug="notice", allow_anonymous=False),
            Board(name="자유게시판", slug="free", allow_anonymous=True),
            Board(name="질문답변", slug="qna", allow_anonymous=True),
        ]
        
        for board in boards:
            db.add(board)
        db.commit()
        print("초기 게시판이 생성되었습니다!")
    
    db.close()

@app.on_event("startup")
async def startup_event():
    create_initial_data()

# ===== BOOK 관련 라우터 =====
@app.post("/books/", response_model=schemas.Book)
async def create_books(
    isbn: str = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    category: Optional[str] = Form(None),
    publisher: Optional[str] = Form(None),
    issue_date: Optional[date] = Form(None),
    detail: Optional[str] = Form(None),
    price: Optional[int] = Form(None),
    cover_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # ISBN 중복 체크
    db_book = db.query(Book).filter(Book.isbn == isbn).first()
    if db_book:
        raise HTTPException(status_code=400, detail="ISBN already registered")
    
    # 이미지 업로드 처리
    cover_image_url = None
    if cover_image:
        try:
            if not cover_image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="Only image files are allowed")
            
            result = cloudinary.uploader.upload(
                cover_image.file,
                folder="book_covers",
                public_id=f"book_{isbn}",
                overwrite=True,
                resource_type="image"
            )
            cover_image_url = result.get("secure_url")
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Image upload failed: {str(e)}")
    
    # 책 데이터 생성
    book_data = {
        "isbn": isbn,
        "title": title, 
        "author": author,
        "category": category,
        "publisher": publisher,
        "issue_date": issue_date,
        "detail": detail,
        "price": price,
        "cover_image_url": cover_image_url
    }
    
    db_book = Book(**book_data)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.get('/books/', response_model=List[schemas.Book])
def get_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = db.query(Book).order_by(Book.created_at.desc()).offset(skip).limit(limit).all()
    return books


@app.get('/books/{book_id}', response_model=schemas.Book)
def get_book_by_id(book_id:int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=schemas.Book)
def update_book_full(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
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
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    # 책 존재 확인
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # 삭제
    db.delete(db_book)
    db.commit()
    return {"message": f"Book {book_id} deleted successfully"}


@app.post("/posts/", response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    """새 글 작성"""
    db_post = Post(
        title=post.title,
        content=post.content,
        author=post.author,
        board_id=post.board_id,
        password=post.password,
        is_notice=post.is_notice,
        is_secret=post.is_secret
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/posts/", response_model=List[schemas.PostResponse])
def get_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """글 목록 조회 - 최신순으로 정렬"""
    posts = db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@app.get("/posts/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """글 상세 조회"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.put("/posts/{post_id}", response_model=schemas.PostResponse)
def update_post(post_id: int, post_update: schemas.PostUpdate, db: Session = Depends(get_db)):
    """글 수정"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    update_data = post_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    return post


@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """글 삭제"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}