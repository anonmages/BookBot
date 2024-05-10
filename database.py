import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    preferences = Column(Text)
    chats = relationship("ChatHistory", order_by="ChatHistory.id", back_populates="user_profile")

    def __repr__(self):
        return f"<UserProfile(username={self.username})>"

class ChatHistory(Base):
    __tablename__ = 'chat_histories'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_profiles.id'))
    chat_text = Column(Text)
    user_profile = relationship("UserProfile", back_populates="chats")

    def __repr__(self):
        return f"<ChatHistory(user_id={self.user_id})>"

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    summary = Column(Text)
    isbn = Column(String(20), unique=True)

    def __repr__(self):
        return f"<Book(title={self.title}, author={self.author})>"

Base.metadata.create_all(engine)

@lru_cache(maxsize=None)
def create_user(username, preferences):
    new_user = UserProfile(username=username, preferences=preferences)
    session.add(new_user)
    session.commit()

@lru_cache(maxsize=None)
def get_user_by_username(username):
    return session.query(UserProfile).filter_by(username=username).first()

def update_user_preferences(username, new_preferences):
    user = get_user_by_username.__wrapped__(username)
    if user:
        user.preferences = new_preferences
        session.commit()
        get_user_by_username.cache_clear()

def delete_user(username):
    user = get_user_by_username.__wrapped__(username)
    if user:
        session.delete(user)
        session.commit()
        get_user_by_username.cache_clear()

@lru_cache(maxsize=None)
def create_book(title, author, summary, isbn):
    new_book = Book(title=title, author=author, summary=summary, isbn=isbn)
    session.add(new_book)
    session.commit()

@lru_cache(maxsize=None)
def get_book_by_title(title):
    return session.query(Book).filter_by(title=title).first()

def add_chat_history(user_id, chat_text):
    new_chat_history = ChatHistory(user_id=user_id, chat_text=chat_text)
    session.add(new_chat_history)
    session.commit()

@lru_cache(maxsize=None)
def get_chat_history_for_user(username):
    user = get_user_by_username(username)
    return user.chats if user else None