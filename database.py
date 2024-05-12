import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
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
    try:
        new_user = UserProfile(username=username, preferences=preferences)
        session.add(new_user)
        session.commit()
    except IntegrityError:
        print(f"User with username '{username}' already exists.")
        session.rollback()
    except SQLAlchemyError as e:
        print(f"Unable to create user: {e}")
        session.rollback()

@lru_cache(maxsize=None)
def get_user_by_username(username):
    try:
        return session.query(UserProfile).filter_by(username=username).first()
    except SQLAlchemyError as e:
        print(f"Error fetching user by username '{username}': {e}")
        return None

def update_user_preferences(username, new_preferences):
    try:
        user = get_user_by_username.__wrapped__(username)
        if user:
            user.preferences = new_preferences
            session.commit()
            get_user_by_username.cache_clear()
        else:
            print(f"No user found with username '{username}'.")
    except SQLAlchemyError as e:
        print(f"Unable to update user preferences: {e}")
        session.rollback()

def delete_user(username):
    try:
        user = get_user_by_username.__wrapped__(username)
        if user:
            session.delete(user)
            session.commit()
            get_user_by_username.cache_clear()
        else:
            print(f"No user found with username '{username}'.")
    except SQLAlchemyError as e:
        print(f"Unable to delete user: {e}")
        session.rollback()

@lru_cache(maxsize=None)
def create_book(title, author, summary, isbn):
    try:
        new_book = Book(title=title, author=author, summary=summary, isbn=isbn)
        session.add(new_book)
        session.commit()
    except IntegrityError:
        print(f"Book with ISBN '{isbn}' already exists.")
        session.rollback()
    except SQLAlchemyError as e:
        print(f"Unable to create book: {e}")
        session.rollback()

@lru_cache(maxsize=None)
def get_book_by_title(title):
    try:
        return session.query(Book).filter_by(title=title).first()
    except SQLAlchemyError as e:
        print(f"Error fetching book by title '{title}': {e}")
        return None

def add_chat_history(user_id, chat_text):
    try:
        new_chat_history = ChatHistory(user_id=user_id, chat_text=chat_text)
        session.add(new_chat_history)
        session.commit()
    except SQLAlchemyError as e:
        print(f"Unable to add chat history: {e}")
        session.rollback()

@lru_cache(maxsize=None)
def get_chat_history_for_user(username):
    try:
        user = get_user_by_username(username)
        return user.chats if user else None
    except SQLAlchemyError as e:
        print(f"Error fetching chat history for user '{username}': {e}")
        return None