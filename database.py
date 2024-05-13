import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

DATABASE_URI = os.environ.get("DATABASE_URL")
Base = declarative_base()
engine = create_engine(DATABASE_URI, echo=True)
SessionManager = sessionmaker(bind=engine)
db_session = SessionManager()

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    preferences = Column(Text)
    chat_history = relationship("ChatEntry", order_by="ChatEntry.id", back_populates="user")

    def __repr__(self):
        return f"<UserProfile(username={self.username})>"

class ChatEntry(Base):
    __tablename__ = 'chat_entries'
    id = Column(Integer, primary_key=True)
    user_profile_id = Column(Integer, ForeignKey('user_profiles.id'))
    message = Column(Text)
    user = relationship("UserProfile", back_populates="chat_history")

    def __repr__(self):
        return f"<ChatEntry(user_profile_id={self.user_profile_id})>"

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
def add_user_profile(username, preferences):
    try:
        user_profile = UserProfile(username=username, preferences=preferences)
        db_session.add(user_profile)
        db_session.commit()
    except IntegrityError:
        print(f"User with username '{username}' already exists.")
        db_session.rollback()
    except SQLAlchemyError as error:
        print(f"Unable to create user profile: {error}")
        db_session.rollback()

@lru_cache(maxsize=None)
def fetch_user_profile_by_username(username):
    try:
        user_profile = db_session.query(UserProfile).filter_by(username=username).first()
        return user_profile
    except SQLAlchemyError as error:
        print(f"Error fetching user profile by username '{username}': {error}")
        return None

def modify_user_preferences(username, updated_preferences):
    try:
        user_profile = fetch_user_profile_by_username.__wrapped__(username)
        if user_profile:
            user_profile.preferences = updated_preferences
            db_session.commit()
            fetch_user_profile_by_username.cache_clear()
        else:
            print(f"No user profile found with username '{username}'.")
    except SQLAlchemyError as error:
        print(f"Unable to update user preferences: {error}")
        db_session.rollback()

def remove_user_profile(username):
    try:
        user_profile = fetch_user_profile_by_username.__wrapped__(username)
        if user_profile:
            db_session.delete(user_profile)
            db_session.commit()
            fetch_user_profile_by_username.cache_clear()
        else:
            print(f"No user profile found with username '{username}'.")
    except SQLAlchemyError as error:
        print(f"Unable to remove user profile: {error}")
        db_session.rollback()

@lru_cache(maxsize=None)
def add_book_entry(title, author, summary, isbn):
    try:
        book_entry = Book(title=title, author=author, summary=summary, isbn=isbn)
        db_session.add(book_entry)
        db_session.commit()
    except IntegrityError:
        print(f"Book with ISBN '{isbn}' already exists.")
        db_session.rollback()
    except SQLAlchemyError as error:
        print(f"Unable to create book entry: {error}")
        db_session.rollback()

@lru_cache(maxsize=None)
def fetch_book_by_title(title):
    try:
        book_entry = db_session.query(Book).filter_by(title=title).first()
        return book_entry
    except SQLAlchemyError as error:
        print(f"Error fetching book by title '{title}': {error}")
        return None

def log_chat_entry(user_id, message):
    try:
        new_chat_entry = ChatEntry(user_profile_id=user_id, message=message)
        db_session.add(new_chat_entry)
        db_session.commit()
    except SQLAlchemyError as error:
        print(f"Unable to log chat entry: {error}")
        db_session.rollback()

@lru_cache(maxsize=None)
def fetch_chat_history_by_username(username):
    try:
        user_profile = fetch_user_profile_by_username(username)
        return user_profile.chat_history if user_profile else None
    except SQLAlchemyError as error:
        print(f"Error fetching chat history for user '{username}': {error}")
        return None