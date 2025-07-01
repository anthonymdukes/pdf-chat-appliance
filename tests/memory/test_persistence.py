"""
Persistence tests for memory layer.
"""
import os
from memory.api import MemoryAPI

def test_persistence_across_restarts(tmp_path):
    db_path = tmp_path / "persist.db"
    # Create and add data
    api1 = MemoryAPI(db_path=str(db_path))
    session = api1.create_session(user_id="persist_user")
    api1.add_message(session_id=session.id, role="user", content="persisted message")
    # Simulate process restart by re-instantiating API
    api2 = MemoryAPI(db_path=str(db_path))
    fetched_session = api2.get_session(session.id)
    assert fetched_session is not None
    messages = api2.get_messages(session.id)
    assert len(messages) == 1
    assert messages[0].content == "persisted message" 