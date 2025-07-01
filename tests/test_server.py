"""
Tests for the Flask server module.
"""

import pytest
from unittest.mock import Mock, patch
from pdfchat.server import QueryServer
from pdfchat.config import Config


class TestQueryServer:
    """Test cases for QueryServer class."""
    
    def test_init_with_default_config(self):
        """Test expected use case: initialization with default config."""
        server = QueryServer()
        assert server.config is not None
        assert server.config.host == "0.0.0.0"
        assert server.config.port == 5000
    
    def test_init_with_custom_config(self):
        """Test edge case: initialization with custom config."""
        custom_config = Config(host="127.0.0.1", port=8080)
        server = QueryServer(custom_config)
        assert server.config.host == "127.0.0.1"
        assert server.config.port == 8080
    
    @patch('pdfchat.server.Flask')
    def test_flask_app_creation(self, mock_flask):
        """Test expected use case: Flask app creation."""
        mock_app = Mock()
        mock_flask.return_value = mock_app
        
        server = QueryServer()
        
        assert server.app == mock_app
        mock_flask.assert_called_once_with(__name__)
    
    def test_health_endpoint(self):
        """Test expected use case: health check endpoint."""
        server = QueryServer()
        
        with server.app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            assert b'healthy' in response.data
    
    def test_index_endpoint(self):
        """Test expected use case: index page endpoint."""
        server = QueryServer()
        
        with server.app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            assert b'PDF Chat Appliance' in response.data
    
    def test_query_endpoint_missing_question(self):
        """Test failure case: query without question."""
        server = QueryServer()
        
        with server.app.test_client() as client:
            response = client.post('/query', json={})
            assert response.status_code == 400
            assert b'Missing' in response.data
    
    def test_query_endpoint_invalid_json(self):
        """Test failure case: invalid JSON in query."""
        server = QueryServer()
        
        with server.app.test_client() as client:
            response = client.post('/query', data='invalid json')
            assert response.status_code == 400
    
    @patch('pdfchat.server.PDFIngestion')
    def test_query_endpoint_success(self, mock_ingestion):
        """Test expected use case: successful query."""
        mock_ingestion_instance = Mock()
        mock_index = Mock()
        mock_query_engine = Mock()
        mock_response = Mock()
        mock_response.__str__ = lambda: "Test answer"
        
        mock_ingestion_instance.load_existing_index.return_value = mock_index
        mock_index.as_query_engine.return_value = mock_query_engine
        mock_query_engine.query.return_value = mock_response
        mock_ingestion.return_value = mock_ingestion_instance
        
        server = QueryServer()
        
        with server.app.test_client() as client:
            response = client.post('/query', json={"question": "What is this?"})
            assert response.status_code == 200
            assert b'Test answer' in response.data
    
    def test_run_with_custom_host_port(self):
        """Test edge case: running with custom host and port."""
        server = QueryServer()
        
        with patch.object(server.app, 'run') as mock_run:
            server.run(host="127.0.0.1", port=8080)
            mock_run.assert_called_once_with(host="127.0.0.1", port=8080, debug=False) 