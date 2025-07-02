"""
Tests for the PDF ingestion module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from pdfchat.ingestion import PDFIngestion
from pdfchat.config import Config


class TestPDFIngestion:
    """Test cases for PDFIngestion class."""
    
    def test_init_with_default_config(self):
        """Test expected use case: initialization with default config."""
        ingestion = PDFIngestion()
        assert ingestion.config is not None
        assert ingestion.config.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    
    def test_init_with_custom_config(self):
        """Test edge case: initialization with custom config."""
        custom_config = Config(embedding_model="custom-model")
        ingestion = PDFIngestion(custom_config)
        assert ingestion.config.embedding_model == "custom-model"
    
    @patch('pdfchat.ingestion.SimpleDirectoryReader')
    def test_load_documents_success(self, mock_reader):
        """Test expected use case: successful document loading."""
        # Create mock documents with required attributes
        mock_doc1 = Mock()
        mock_doc1.text = "This is test document 1"
        mock_doc1.doc_id = "doc1"
        mock_doc1.id_ = "doc1"
        mock_doc1.metadata = {"filename": "test1.pdf"}
        
        mock_doc2 = Mock()
        mock_doc2.text = "This is test document 2"
        mock_doc2.doc_id = "doc2"
        mock_doc2.id_ = "doc2"
        mock_doc2.metadata = {"filename": "test2.pdf"}
        
        mock_docs = [mock_doc1, mock_doc2]
        mock_reader.return_value.load_data.return_value = mock_docs
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a dummy PDF file
            pdf_file = os.path.join(temp_dir, "test.pdf")
            with open(pdf_file, 'w') as f:
                f.write("dummy pdf content")
            
            ingestion = PDFIngestion()
            documents = ingestion.load_documents(temp_dir)
            
            assert len(documents) == 2
            mock_reader.assert_called_once_with(temp_dir, recursive=True)
    
    def test_load_documents_nonexistent_directory(self):
        """Test failure case: non-existent directory."""
        ingestion = PDFIngestion()
        
        with pytest.raises(FileNotFoundError):
            ingestion.load_documents("nonexistent_dir")
    
    @patch('pdfchat.ingestion.VectorStoreIndex')
    @patch('pdfchat.ingestion.QdrantVectorStore')
    @patch('pdfchat.ingestion.QdrantClient')
    @patch('pdfchat.ingestion.StorageContext')
    def test_create_vector_store(self, mock_storage, mock_client, mock_vector_store, mock_index):
        """Test expected use case: vector store creation."""
        # Create mock documents with required attributes
        mock_doc = Mock()
        mock_doc.text = "Test document"
        mock_doc.doc_id = "doc1"
        mock_doc.id_ = "doc1"
        mock_doc.metadata = {"filename": "test.pdf"}
        mock_docs = [mock_doc]
        
        mock_index_instance = Mock()
        mock_index.from_documents.return_value = mock_index_instance
        
        ingestion = PDFIngestion()
        result = ingestion.create_vector_store(mock_docs)
        
        assert result == mock_index_instance
        mock_index.from_documents.assert_called_once()
        mock_index_instance.storage_context.persist.assert_called_once()
    
    @patch('pdfchat.ingestion.PDFIngestion.load_documents')
    @patch('pdfchat.ingestion.PDFIngestion.create_vector_store')
    def test_ingest_pdfs_workflow(self, mock_create_store, mock_load_docs):
        """Test expected use case: complete ingestion workflow."""
        mock_docs = [Mock()]
        mock_index = Mock()
        mock_load_docs.return_value = mock_docs
        mock_create_store.return_value = mock_index
        
        with tempfile.TemporaryDirectory() as temp_dir:
            ingestion = PDFIngestion()
            result = ingestion.ingest_pdfs(temp_dir)
            
            assert result == mock_index
            mock_load_docs.assert_called_once_with(temp_dir)
            mock_create_store.assert_called_once_with(mock_docs) 