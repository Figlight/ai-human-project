from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from backend.app.db.database import Base

beijing_tz = timezone(timedelta(hours=8))


def get_beijing_now():
    return datetime.now(beijing_tz).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    salt = Column(String(64), nullable=False)
    role = Column(String(16), default="user")  # 'user' or 'admin'
    token = Column(String(128), index=True, nullable=True)
    created_at = Column(DateTime, default=get_beijing_now)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(64), index=True, nullable=False)
    role = Column(String(16), nullable=False)
    content = Column(Text, nullable=False)
    emotion = Column(String(16), default="neutral")
    audio_path = Column(String(256))
    created_at = Column(DateTime, default=get_beijing_now)

    user = relationship("User", backref="conversations")


class QAItem(Base):
    __tablename__ = "qa_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(64), default="景区概况")
    created_at = Column(DateTime, default=get_beijing_now)
    updated_at = Column(DateTime, default=get_beijing_now, onupdate=get_beijing_now)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    file_path = Column(String(512))
    file_size = Column(String(32))
    pages = Column(Integer, default=0)
    chunks = Column(Integer, default=0)
    status = Column(String(32), default="indexing")
    created_at = Column(DateTime, default=get_beijing_now)


class VisitorFeedback(Base):
    __tablename__ = "visitor_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), index=True)
    satisfaction = Column(Integer)
    emotion = Column(String(16))
    keywords = Column(JSON)
    suggestion = Column(Text)
    created_at = Column(DateTime, default=get_beijing_now)


class DHConfig(Base):
    __tablename__ = "dh_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), default="小导")
    title = Column(String(64), default="智能导游")
    character = Column(String(32), default="guide1")
    voice = Column(String(64), default="zh-CN-XiaoxiaoNeural")
    outfit = Column(String(32), default="outfit1")
    speed = Column(Float, default=1.0)
