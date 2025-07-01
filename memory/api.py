"""
Unified memory API for PDF Chat Appliance.

This module provides a backend-agnostic interface for all memory operations.
"""

from .sqlite_backend import SQLiteMemoryBackend

class MemoryAPI:
    """Unified API for persistent memory operations."""
    def __init__(self, backend=None, db_path="data/memory.db"):
        self.backend = backend or SQLiteMemoryBackend(db_path=db_path)

    # Session operations
    def create_session(self, **kwargs):
        return self.backend.add_session(**kwargs)

    def get_session(self, session_id):
        return self.backend.get_session(session_id)

    def list_sessions(self, user_id=None):
        return self.backend.list_sessions(user_id=user_id)

    # Message operations
    def add_message(self, **kwargs):
        return self.backend.add_message(**kwargs)

    def get_messages(self, session_id):
        return self.backend.get_messages(session_id)

    # Document insight operations
    def add_document_insight(self, **kwargs):
        return self.backend.add_document_insight(**kwargs)

    def get_document_insight(self, doc_id):
        return self.backend.get_document_insight(doc_id) 