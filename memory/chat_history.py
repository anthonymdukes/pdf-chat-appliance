"""
Persistent chat history for PDF Chat Appliance.
Stores chat messages and responses by user and document using SQLite.
"""

import datetime
import os
from typing import List

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class ChatMessage(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=True)
    document_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)


class ChatHistoryDB:
    def __init__(self, db_path: str = "data/chat_history.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, future=True)

    def add_message(self, user_id: str, document_id: str, message: str, response: str):
        with self.Session() as db:
            chat = ChatMessage(
                user_id=user_id,
                document_id=document_id,
                message=message,
                response=response,
            )
            db.add(chat)
            db.commit()

    def get_history(
        self, user_id: str, document_id: str, limit: int = 10
    ) -> List[ChatMessage]:
        with self.Session() as db:
            q = db.query(ChatMessage).filter_by(
                user_id=user_id, document_id=document_id
            )
            q = q.order_by(ChatMessage.timestamp.desc()).limit(limit)
            return list(reversed(q.all()))
