"""
SQLite backend for long-term memory using SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Session as SessionModel, Message, DocumentInsight

class SQLiteMemoryBackend:
    """SQLite-backed persistent memory for user sessions, messages, and document insights."""
    def __init__(self, db_path="data/memory.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, future=True)

    def add_session(self, **kwargs):
        with self.Session() as db:
            session = SessionModel(**kwargs)
            db.add(session)
            db.commit()
            return session

    def add_message(self, **kwargs):
        with self.Session() as db:
            message = Message(**kwargs)
            db.add(message)
            db.commit()
            return message

    def add_document_insight(self, **kwargs):
        with self.Session() as db:
            insight = DocumentInsight(**kwargs)
            db.add(insight)
            db.commit()
            return insight

    def get_session(self, session_id):
        with self.Session() as db:
            return db.get(SessionModel, session_id)

    def get_messages(self, session_id):
        with self.Session() as db:
            return db.query(Message).filter_by(session_id=session_id).all()

    def get_document_insight(self, doc_id):
        with self.Session() as db:
            return db.query(DocumentInsight).filter_by(doc_id=doc_id).first()

    def list_sessions(self, user_id=None):
        with self.Session() as db:
            q = db.query(SessionModel)
            if user_id:
                q = q.filter_by(user_id=user_id)
            return q.all() 