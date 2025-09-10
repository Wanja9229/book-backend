from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(17), unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    category = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    issue_date = Column(Date, nullable=True)
    detail = Column(Text, nullable=True)
    price = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())