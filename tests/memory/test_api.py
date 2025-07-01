"""
Integration tests for memory.api MemoryAPI.
"""
import pytest
import os
from memory.api import MemoryAPI

def test_create_and_get_session(tmp_path):
    db_path = tmp_path / "test_memory.db"
    api = MemoryAPI(db_path=str(db_path))
    session = api.create_session(user_id="userA")
    assert session.id is not None
    fetched = api.get_session(session.id)
    assert fetched.id == session.id
    assert fetched.user_id == "userA"

def test_add_and_get_message(tmp_path):
    db_path = tmp_path / "test_memory.db"
    api = MemoryAPI(db_path=str(db_path))
    session = api.create_session(user_id="userB")
    msg = api.add_message(session_id=session.id, role="user", content="Hi!")
    assert msg.id is not None
    messages = api.get_messages(session.id)
    assert len(messages) == 1
    assert messages[0].content == "Hi!"

def test_add_and_get_document_insight(tmp_path):
    db_path = tmp_path / "test_memory.db"
    api = MemoryAPI(db_path=str(db_path))
    insight = api.add_document_insight(doc_id="docX", summary="S", key_findings="K", tags="T")
    assert insight.id is not None
    fetched = api.get_document_insight("docX")
    assert fetched.doc_id == "docX"
    assert fetched.summary == "S"

def test_list_sessions(tmp_path):
    db_path = tmp_path / "test_memory.db"
    api = MemoryAPI(db_path=str(db_path))
    s1 = api.create_session(user_id="user1")
    s2 = api.create_session(user_id="user2")
    all_sessions = api.list_sessions()
    assert len(all_sessions) == 2
    user1_sessions = api.list_sessions(user_id="user1")
    assert len(user1_sessions) == 1
    assert user1_sessions[0].user_id == "user1" 