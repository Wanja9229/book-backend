from pydantic import BaseModel, Field  
from datetime import datetime, date
from typing import Optional

class BookBase(BaseModel):
    isbn:str = Field(..., min_length=1, max_length=17, pattern="^[0-9-]+$")  #도서 번호
    title:str #도서 제목
    author:str #지은이
    category:Optional[str] = None  #분야
    publisher:Optional[str] = None  #출판사
    issue_date:Optional[date] = None  #출간일
    detail:Optional[str] = None #판형 및 쪽수
    price:Optional[int] = None  #가격
    cover_image_url: Optional[str] = None #이미지 경로

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    isbn:Optional[str] = Field(None, min_length=1, max_length=17, pattern="^[0-9-]+$")  #도서 번호
    title:Optional[str] = None #도서 제목
    author:Optional[str] = None #지은이
    category:Optional[str] = None  #분야
    publisher:Optional[str] = None  #출판사
    issue_date:Optional[date] = None  #출간일
    detail:Optional[str] = None #판형 및 쪽수
    price:Optional[int] = None  #가격

class Book(BookBase):
    id: int  # PK
    created_at: datetime  # 등록일시
    updated_at: Optional[datetime] = None  # 수정일시
    
    class Config:
        from_attributes = True  # DB → Pydantic 자동변환
