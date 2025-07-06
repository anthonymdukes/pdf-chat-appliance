"""
Unit tests for memory.models ORM models.
"""


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from memory.models import Base, DocumentInsight, Message, Session


def in_memory_db():
    engine = create_engine("sqlite:///:memory:", echo=False, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)


def test_session_creation():
    SessionLocal = in_memory_db()
    with SessionLocal() as db:
        session = Session(user_id="user1")
        db.add(session)
        db.commit()
        assert session.id is not None
        assert session.start_time is not None


def test_message_relationship():
    SessionLocal = in_memory_db()
    with SessionLocal() as db:
        session = Session(user_id="user2")
        db.add(session)
        db.commit()
        message = Message(session_id=session.id, role="user", content="Hello!")
        db.add(message)
        db.commit()
        assert message.session_id == session.id
        assert message.role == "user"
        assert message.content == "Hello!"
        # Relationship
        assert message.session.id == session.id


def test_document_insight_creation():
    SessionLocal = in_memory_db()
    with SessionLocal() as db:
        insight = DocumentInsight(
            doc_id="doc1", summary="Summary", key_findings="Findings", tags="tag1,tag2"
        )
        db.add(insight)
        db.commit()
        assert insight.id is not None
        assert insight.doc_id == "doc1"
        assert insight.summary == "Summary"
        assert insight.last_accessed is not None
