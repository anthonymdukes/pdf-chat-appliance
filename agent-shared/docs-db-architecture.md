# Structured Documentation Management - Complete Architecture

**Date:** 2025-07-06  
**Status:** Paper Architecture Exercise (Implementation On Hold Until Repo Restructure)  
**Architects:** system-architect, docs-maintainer, agent-orchestrator, infra-consulting, qa-tester, core

---

## Executive Summary

This document provides a complete architectural specification for a structured documentation management system using a lightweight database layer alongside Markdown. The system is designed to enhance searchability, agent handoff efficiency, and cross-file indexing while maintaining backward compatibility with existing workflows.

**Implementation Status:** Paper architecture complete - deployment postponed until repository restructure completion.

---

## Database Schema Specification

### Core Tables

#### documents
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    file_type TEXT NOT NULL CHECK (file_type IN ('md', 'mdc', 'yaml', 'json', 'txt')),
    title TEXT,
    content_hash TEXT NOT NULL,
    content_length INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_indexed_at TIMESTAMP,
    agent_owner TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived', 'draft', 'deleted')),
    priority INTEGER DEFAULT 1,
    tags TEXT, -- JSON array of tags
    summary TEXT,
    word_count INTEGER,
    line_count INTEGER
);

CREATE INDEX idx_documents_file_path ON documents(file_path);
CREATE INDEX idx_documents_agent_owner ON documents(agent_owner);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_updated_at ON documents(updated_at);
```

#### document_metadata
```sql
CREATE TABLE document_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT,
    value_type TEXT DEFAULT 'string' CHECK (value_type IN ('string', 'json', 'number', 'date', 'boolean')),
    confidence REAL DEFAULT 1.0,
    source TEXT DEFAULT 'extracted', -- 'extracted', 'manual', 'inferred'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, key)
);

CREATE INDEX idx_metadata_document_id ON document_metadata(document_id);
CREATE INDEX idx_metadata_key ON document_metadata(key);
```

#### document_relationships
```sql
CREATE TABLE document_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    target_document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL CHECK (relationship_type IN ('references', 'depends_on', 'similar_to', 'part_of', 'extends', 'implements', 'tests')),
    strength REAL DEFAULT 1.0 CHECK (strength >= 0.0 AND strength <= 1.0),
    confidence REAL DEFAULT 1.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    metadata JSON, -- Additional relationship metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_document_id, target_document_id, relationship_type)
);

CREATE INDEX idx_relationships_source ON document_relationships(source_document_id);
CREATE INDEX idx_relationships_target ON document_relationships(target_document_id);
CREATE INDEX idx_relationships_type ON document_relationships(relationship_type);
```

#### document_embeddings
```sql
CREATE TABLE document_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    embedding_model TEXT NOT NULL,
    embedding_version TEXT NOT NULL,
    embedding_data BLOB NOT NULL,
    embedding_dimensions INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, embedding_model, embedding_version)
);

CREATE INDEX idx_embeddings_document_id ON document_embeddings(document_id);
CREATE INDEX idx_embeddings_model ON document_embeddings(embedding_model);
```

#### agent_sessions
```sql
CREATE TABLE agent_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    agent_name TEXT NOT NULL,
    session_type TEXT DEFAULT 'workflow' CHECK (session_type IN ('workflow', 'training', 'review', 'maintenance')),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'failed', 'paused')),
    summary TEXT,
    metadata JSON, -- Session-specific metadata
    parent_session_id INTEGER REFERENCES agent_sessions(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_agent_name ON agent_sessions(agent_name);
CREATE INDEX idx_sessions_status ON agent_sessions(status);
CREATE INDEX idx_sessions_start_time ON agent_sessions(start_time);
```

#### session_activities
```sql
CREATE TABLE session_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES agent_sessions(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL CHECK (activity_type IN ('read', 'write', 'search', 'analyze', 'create', 'update', 'delete', 'index')),
    document_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    details JSON, -- Activity-specific details
    metadata JSON -- Additional activity metadata
);

CREATE INDEX idx_activities_session_id ON session_activities(session_id);
CREATE INDEX idx_activities_type ON session_activities(activity_type);
CREATE INDEX idx_activities_timestamp ON session_activities(timestamp);
CREATE INDEX idx_activities_document_id ON session_activities(document_id);
```

#### search_queries
```sql
CREATE TABLE search_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER REFERENCES agent_sessions(id) ON DELETE SET NULL,
    query_text TEXT NOT NULL,
    query_type TEXT DEFAULT 'hybrid' CHECK (query_type IN ('text', 'semantic', 'hybrid', 'metadata')),
    filters JSON,
    results_count INTEGER,
    response_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_queries_session_id ON search_queries(session_id);
CREATE INDEX idx_queries_created_at ON search_queries(created_at);
```

---

## Integration Patterns

### Markdown-to-Database Synchronization

#### Automatic Metadata Extraction
```python
class MarkdownMetadataExtractor:
    """Extract metadata from markdown files automatically."""
    
    def extract_metadata(self, file_path: str, content: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from markdown content."""
        metadata = {
            'title': self._extract_title(content),
            'agent_owner': self._extract_agent_owner(content),
            'tags': self._extract_tags(content),
            'summary': self._extract_summary(content),
            'last_updated': self._extract_last_updated(content),
            'word_count': self._count_words(content),
            'line_count': self._count_lines(content),
            'has_code_blocks': self._has_code_blocks(content),
            'has_tables': self._has_tables(content),
            'has_images': self._has_images(content),
            'complexity_score': self._calculate_complexity(content)
        }
        return metadata
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content."""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return None
    
    def _extract_agent_owner(self, content: str) -> str:
        """Extract agent owner from content patterns."""
        patterns = [
            r'@(\w+(-\w+)*)',  # @agent-name
            r'Agent:\s*(\w+(-\w+)*)',  # Agent: agent-name
            r'(\w+(-\w+)*)\s+Agent'  # agent-name Agent
        ]
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        return None
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content."""
        tags = []
        # Look for tag patterns
        tag_patterns = [
            r'#(\w+)',  # #tag
            r'tags?:\s*\[([^\]]+)\]',  # tags: [tag1, tag2]
            r'tags?:\s*([^\n]+)'  # tags: tag1, tag2
        ]
        for pattern in tag_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if ',' in match:
                    tags.extend([tag.strip() for tag in match.split(',')])
                else:
                    tags.append(match.strip())
        return list(set(tags))
    
    def _extract_summary(self, content: str) -> str:
        """Extract summary from content."""
        # Look for summary in front matter or first paragraph
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().lower().startswith('summary:'):
                return line.split(':', 1)[1].strip()
            elif line.strip().lower().startswith('description:'):
                return line.split(':', 1)[1].strip()
        
        # Extract first meaningful paragraph
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('---'):
                return line.strip()[:200] + ('...' if len(line.strip()) > 200 else '')
        return None
```

#### Manual Metadata (Front Matter)
```yaml
---
title: "Documentation Strategy Review"
agent_owner: "docs-maintainer"
tags: ["documentation", "strategy", "review", "architecture"]
summary: "Comprehensive evaluation of documentation structure and standards"
last_updated: "2025-07-06"
status: "active"
priority: 2
complexity: "medium"
dependencies: ["DOCUMENT_RULES.md", "session_notes.md"]
related_docs: ["agent-shared/docs-review.md", "docs/DOC_CHANGELOG.md"]
---
```

### Agent Workflow Integration

#### Session Management
```python
class AgentSessionManager:
    """Manage agent sessions and activity tracking."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.current_session_id = None
    
    def start_session(self, agent_name: str, session_type: str = 'workflow') -> str:
        """Start a new agent session."""
        session_id = f"{agent_name}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        query = """
        INSERT INTO agent_sessions (session_id, agent_name, session_type, status)
        VALUES (?, ?, ?, 'active')
        """
        self.db.execute(query, (session_id, agent_name, session_type))
        self.db.commit()
        
        self.current_session_id = session_id
        return session_id
    
    def log_activity(self, activity_type: str, document_id: int = None, 
                    details: Dict = None, metadata: Dict = None):
        """Log an activity in the current session."""
        if not self.current_session_id:
            raise ValueError("No active session")
        
        query = """
        INSERT INTO session_activities 
        (session_id, activity_type, document_id, details, metadata)
        VALUES (?, ?, ?, ?, ?)
        """
        self.db.execute(query, (
            self.current_session_id,
            activity_type,
            document_id,
            json.dumps(details) if details else None,
            json.dumps(metadata) if metadata else None
        ))
        self.db.commit()
    
    def end_session(self, summary: str = None, metadata: Dict = None):
        """End the current session."""
        if not self.current_session_id:
            return
        
        query = """
        UPDATE agent_sessions 
        SET end_time = CURRENT_TIMESTAMP, status = 'completed', 
            summary = ?, metadata = ?
        WHERE session_id = ?
        """
        self.db.execute(query, (
            summary,
            json.dumps(metadata) if metadata else None,
            self.current_session_id
        ))
        self.db.commit()
        
        self.current_session_id = None
```

#### Document Indexing Integration
```python
class DocumentIndexer:
    """Integrate document indexing with agent workflows."""
    
    def __init__(self, db_connection, embedding_model=None):
        self.db = db_connection
        self.embedding_model = embedding_model
        self.extractor = MarkdownMetadataExtractor()
    
    def index_document(self, file_path: str, content: str, 
                      agent_session_id: str = None) -> int:
        """Index a document and return its ID."""
        # Calculate content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Check if document already exists and is unchanged
        existing = self.db.execute(
            "SELECT id, content_hash FROM documents WHERE file_path = ?",
            (file_path,)
        ).fetchone()
        
        if existing and existing[1] == content_hash:
            # Document unchanged, update last_indexed_at
            self.db.execute(
                "UPDATE documents SET last_indexed_at = CURRENT_TIMESTAMP WHERE id = ?",
                (existing[0],)
            )
            self.db.commit()
            return existing[0]
        
        # Extract metadata
        metadata = self.extractor.extract_metadata(file_path, content)
        
        # Insert or update document
        if existing:
            # Update existing document
            query = """
            UPDATE documents SET 
                title = ?, content_hash = ?, content_length = ?, 
                updated_at = CURRENT_TIMESTAMP, last_indexed_at = CURRENT_TIMESTAMP,
                agent_owner = ?, status = ?, tags = ?, summary = ?,
                word_count = ?, line_count = ?
            WHERE id = ?
            """
            self.db.execute(query, (
                metadata.get('title'),
                content_hash,
                len(content),
                metadata.get('agent_owner'),
                'active',
                json.dumps(metadata.get('tags', [])),
                metadata.get('summary'),
                metadata.get('word_count'),
                metadata.get('line_count'),
                existing[0]
            ))
            document_id = existing[0]
        else:
            # Insert new document
            query = """
            INSERT INTO documents 
            (file_path, file_type, title, content_hash, content_length,
             agent_owner, tags, summary, word_count, line_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db.execute(query, (
                file_path,
                self._get_file_type(file_path),
                metadata.get('title'),
                content_hash,
                len(content),
                metadata.get('agent_owner'),
                json.dumps(metadata.get('tags', [])),
                metadata.get('summary'),
                metadata.get('word_count'),
                metadata.get('line_count')
            ))
            document_id = self.db.lastrowid
        
        # Store metadata
        self._store_metadata(document_id, metadata)
        
        # Generate embeddings if model available
        if self.embedding_model:
            self._generate_embeddings(document_id, content)
        
        # Log activity if session provided
        if agent_session_id:
            self._log_indexing_activity(agent_session_id, document_id, file_path)
        
        self.db.commit()
        return document_id
    
    def _store_metadata(self, document_id: int, metadata: Dict):
        """Store extracted metadata in document_metadata table."""
        for key, value in metadata.items():
            if key in ['title', 'content_hash', 'content_length', 'agent_owner', 
                      'tags', 'summary', 'word_count', 'line_count']:
                continue  # These are stored in main documents table
            
            if value is not None:
                query = """
                INSERT OR REPLACE INTO document_metadata 
                (document_id, key, value, value_type, source)
                VALUES (?, ?, ?, ?, 'extracted')
                """
                value_type = self._infer_value_type(value)
                self.db.execute(query, (document_id, key, str(value), value_type))
    
    def _generate_embeddings(self, document_id: int, content: str):
        """Generate and store embeddings for the document."""
        if not self.embedding_model:
            return
        
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(content)
            
            # Store embedding
            query = """
            INSERT OR REPLACE INTO document_embeddings 
            (document_id, embedding_model, embedding_version, embedding_data, embedding_dimensions)
            VALUES (?, ?, ?, ?, ?)
            """
            self.db.execute(query, (
                document_id,
                'sentence-transformers',
                '1.0',
                embedding.tobytes(),
                len(embedding)
            ))
        except Exception as e:
            # Log embedding generation error but don't fail indexing
            print(f"Error generating embeddings for document {document_id}: {e}")
```

---

## Data Ingestion and Query Lifecycle

### Ingestion Pipeline

#### 1. File Discovery
```python
class FileDiscoveryService:
    """Discover and monitor documentation files."""
    
    def __init__(self, root_paths: List[str]):
        self.root_paths = root_paths
        self.file_patterns = ['*.md', '*.mdc', '*.yaml', '*.yml', '*.json']
    
    def discover_files(self) -> List[str]:
        """Discover all documentation files in monitored paths."""
        files = []
        for root_path in self.root_paths:
            for pattern in self.file_patterns:
                files.extend(glob.glob(os.path.join(root_path, '**', pattern), recursive=True))
        return files
    
    def watch_for_changes(self, callback):
        """Watch for file changes and trigger callback."""
        # Implementation would use watchdog or similar library
        pass
```

#### 2. Content Processing
```python
class ContentProcessor:
    """Process and validate document content."""
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single file and return structured data."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract front matter if present
            front_matter, content_body = self._extract_front_matter(content)
            
            # Validate content
            validation_result = self._validate_content(content_body, file_path)
            
            return {
                'file_path': file_path,
                'content': content_body,
                'front_matter': front_matter,
                'validation': validation_result,
                'file_size': len(content),
                'encoding': 'utf-8'
            }
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'validation': {'valid': False, 'errors': [str(e)]}
            }
    
    def _extract_front_matter(self, content: str) -> Tuple[Dict, str]:
        """Extract YAML front matter from markdown content."""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    front_matter = yaml.safe_load(parts[1])
                    return front_matter or {}, parts[2].lstrip('\n')
                except yaml.YAMLError:
                    pass
        return {}, content
    
    def _validate_content(self, content: str, file_path: str) -> Dict:
        """Validate document content."""
        errors = []
        warnings = []
        
        # Check for common issues
        if not content.strip():
            errors.append("Empty content")
        
        if len(content) > 1000000:  # 1MB limit
            warnings.append("Large file size")
        
        # Check for markdownlint issues (if available)
        try:
            lint_result = markdownlint.check_string(content)
            if lint_result:
                warnings.extend([f"Markdown lint: {issue}" for issue in lint_result])
        except:
            pass  # markdownlint not available
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
```

#### 3. Indexing Pipeline
```python
class IndexingPipeline:
    """Complete indexing pipeline for documents."""
    
    def __init__(self, db_connection, embedding_model=None):
        self.db = db_connection
        self.indexer = DocumentIndexer(db_connection, embedding_model)
        self.processor = ContentProcessor()
        self.discovery = FileDiscoveryService(['docs/', 'agent-shared/', 'training/'])
    
    def run_full_index(self, agent_session_id: str = None):
        """Run full indexing of all discovered files."""
        files = self.discovery.discover_files()
        
        indexed_count = 0
        error_count = 0
        
        for file_path in files:
            try:
                # Process file
                file_data = self.processor.process_file(file_path)
                
                if file_data.get('error'):
                    error_count += 1
                    continue
                
                if not file_data['validation']['valid']:
                    error_count += 1
                    continue
                
                # Index document
                document_id = self.indexer.index_document(
                    file_path, 
                    file_data['content'], 
                    agent_session_id
                )
                
                indexed_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"Error indexing {file_path}: {e}")
        
        return {
            'indexed_count': indexed_count,
            'error_count': error_count,
            'total_files': len(files)
        }
    
    def run_incremental_index(self, changed_files: List[str], agent_session_id: str = None):
        """Run incremental indexing of changed files."""
        indexed_count = 0
        error_count = 0
        
        for file_path in changed_files:
            try:
                # Process file
                file_data = self.processor.process_file(file_path)
                
                if file_data.get('error') or not file_data['validation']['valid']:
                    error_count += 1
                    continue
                
                # Index document
                document_id = self.indexer.index_document(
                    file_path, 
                    file_data['content'], 
                    agent_session_id
                )
                
                indexed_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"Error indexing {file_path}: {e}")
        
        return {
            'indexed_count': indexed_count,
            'error_count': error_count,
            'total_files': len(changed_files)
        }
```

### Query Lifecycle

#### 1. Query Processing
```python
class QueryProcessor:
    """Process and optimize search queries."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def process_query(self, query_text: str, query_type: str = 'hybrid', 
                     filters: Dict = None, session_id: str = None) -> Dict:
        """Process a search query and return results."""
        start_time = time.time()
        
        try:
            # Parse and optimize query
            parsed_query = self._parse_query(query_text)
            
            # Apply filters
            applied_filters = self._apply_filters(filters or {})
            
            # Execute search based on type
            if query_type == 'text':
                results = self._text_search(parsed_query, applied_filters)
            elif query_type == 'semantic':
                results = self._semantic_search(parsed_query, applied_filters)
            elif query_type == 'hybrid':
                results = self._hybrid_search(parsed_query, applied_filters)
            else:
                results = self._metadata_search(parsed_query, applied_filters)
            
            # Post-process results
            processed_results = self._post_process_results(results)
            
            # Log query
            response_time = int((time.time() - start_time) * 1000)
            self._log_query(session_id, query_text, query_type, filters, 
                           len(processed_results), response_time, True)
            
            return {
                'results': processed_results,
                'total_count': len(processed_results),
                'response_time_ms': response_time,
                'query_type': query_type,
                'filters_applied': applied_filters
            }
            
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            self._log_query(session_id, query_text, query_type, filters, 
                           0, response_time, False, str(e))
            raise
    
    def _parse_query(self, query_text: str) -> Dict:
        """Parse and optimize query text."""
        # Basic query parsing
        query_parts = query_text.split()
        
        # Extract potential tags
        tags = [part for part in query_parts if part.startswith('#')]
        
        # Extract potential agent names
        agents = [part for part in query_parts if '@' in part]
        
        # Extract potential file types
        file_types = [part for part in query_parts if '.' in part and len(part) <= 10]
        
        return {
            'original': query_text,
            'terms': [part for part in query_parts if not part.startswith('#') and '@' not in part],
            'tags': tags,
            'agents': agents,
            'file_types': file_types
        }
    
    def _apply_filters(self, filters: Dict) -> Dict:
        """Apply and validate search filters."""
        applied_filters = {}
        
        if 'agent_owner' in filters:
            applied_filters['agent_owner'] = filters['agent_owner']
        
        if 'file_type' in filters:
            applied_filters['file_type'] = filters['file_type']
        
        if 'status' in filters:
            applied_filters['status'] = filters['status']
        
        if 'date_range' in filters:
            applied_filters['date_range'] = filters['date_range']
        
        if 'tags' in filters:
            applied_filters['tags'] = filters['tags']
        
        return applied_filters
    
    def _text_search(self, parsed_query: Dict, filters: Dict) -> List[Dict]:
        """Perform text-based search."""
        query = """
        SELECT d.*, 
               CASE 
                   WHEN d.title LIKE ? THEN 3
                   WHEN d.summary LIKE ? THEN 2
                   ELSE 1
               END as relevance_score
        FROM documents d
        WHERE d.status = 'active'
        AND (d.title LIKE ? OR d.summary LIKE ? OR d.tags LIKE ?)
        """
        
        search_term = f"%{parsed_query['original']}%"
        params = [search_term, search_term, search_term, search_term, search_term]
        
        # Add filters
        if 'agent_owner' in filters:
            query += " AND d.agent_owner = ?"
            params.append(filters['agent_owner'])
        
        if 'file_type' in filters:
            query += " AND d.file_type = ?"
            params.append(filters['file_type'])
        
        query += " ORDER BY relevance_score DESC, d.updated_at DESC"
        
        cursor = self.db.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def _semantic_search(self, parsed_query: Dict, filters: Dict) -> List[Dict]:
        """Perform semantic search using embeddings."""
        # This would require vector similarity search
        # Implementation depends on the embedding model and vector database
        return []
    
    def _hybrid_search(self, parsed_query: Dict, filters: Dict) -> List[Dict]:
        """Perform hybrid search combining text and semantic."""
        text_results = self._text_search(parsed_query, filters)
        semantic_results = self._semantic_search(parsed_query, filters)
        
        # Combine and rank results
        combined = self._combine_results(text_results, semantic_results)
        return combined
    
    def _metadata_search(self, parsed_query: Dict, filters: Dict) -> List[Dict]:
        """Search by metadata only."""
        query = """
        SELECT d.*
        FROM documents d
        JOIN document_metadata dm ON d.id = dm.document_id
        WHERE d.status = 'active'
        AND dm.key = ? AND dm.value LIKE ?
        """
        
        results = []
        for term in parsed_query['terms']:
            cursor = self.db.execute(query, ('tags', f"%{term}%"))
            results.extend([dict(row) for row in cursor.fetchall()])
        
        return results
    
    def _log_query(self, session_id: str, query_text: str, query_type: str,
                   filters: Dict, results_count: int, response_time: int,
                   success: bool, error_message: str = None):
        """Log search query for analytics."""
        query = """
        INSERT INTO search_queries 
        (session_id, query_text, query_type, filters, results_count, 
         response_time_ms, success, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute(query, (
            session_id,
            query_text,
            query_type,
            json.dumps(filters) if filters else None,
            results_count,
            response_time,
            success,
            error_message
        ))
        self.db.commit()
```

---

## Docker Persistence Planning

### Volume Configuration

#### Named Volume Approach
```yaml
# docker-compose.yml
version: '3.8'
services:
  pdf-chat-appliance:
    build: .
    volumes:
      # Named volume for database persistence
      - agent_docs_db:/app/agent-memory/docs-db
      # Named volume for embeddings cache
      - agent_embeddings_cache:/app/agent-memory/embeddings
      # Bind mount for source code
      - .:/app/src
      # Bind mount for shared agent directory
      - ./agent-shared:/app/agent-shared
    environment:
      - DOCS_DB_PATH=/app/agent-memory/docs-db/agent-docs-index.db
      - EMBEDDINGS_CACHE_PATH=/app/agent-memory/embeddings
      - AGENT_SHARED_PATH=/app/agent-shared

volumes:
  agent_docs_db:
    driver: local
  agent_embeddings_cache:
    driver: local
```

#### Bind Mount Approach
```yaml
# docker-compose.yml
version: '3.8'
services:
  pdf-chat-appliance:
    build: .
    volumes:
      # Bind mount for database and memory
      - ./agent-memory:/app/agent-memory
      # Bind mount for source code
      - .:/app/src
      # Bind mount for shared agent directory
      - ./agent-shared:/app/agent-shared
    environment:
      - DOCS_DB_PATH=/app/agent-memory/docs-db/agent-docs-index.db
      - EMBEDDINGS_CACHE_PATH=/app/agent-memory/embeddings
      - AGENT_SHARED_PATH=/app/agent-shared
```

### Directory Structure
```
agent-memory/
├── docs-db/
│   ├── agent-docs-index.db          # SQLite database
│   ├── agent-docs-index.db-shm      # SQLite shared memory
│   ├── agent-docs-index.db-wal      # SQLite write-ahead log
│   └── backups/                     # Database backups
├── embeddings/
│   ├── cache/                       # Embedding cache
│   └── models/                      # Local embedding models
└── logs/
    ├── indexing.log                 # Indexing operations log
    ├── queries.log                  # Search queries log
    └── sessions.log                 # Agent sessions log
```

### Dockerfile Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/agent-memory/docs-db \
    /app/agent-memory/embeddings/cache \
    /app/agent-memory/embeddings/models \
    /app/agent-memory/logs

# Copy application code
COPY . /app/src/

# Set environment variables
ENV DOCS_DB_PATH=/app/agent-memory/docs-db/agent-docs-index.db
ENV EMBEDDINGS_CACHE_PATH=/app/agent-memory/embeddings
ENV AGENT_SHARED_PATH=/app/agent-shared

# Initialize database
RUN python /app/src/scripts/init_docs_db.py

# Expose ports
EXPOSE 8000

# Start application
CMD ["python", "/app/src/run_server.py"]
```

### Database Initialization Script
```python
# scripts/init_docs_db.py
import sqlite3
import os
from pathlib import Path

def init_database():
    """Initialize the documentation database."""
    db_path = os.getenv('DOCS_DB_PATH', '/app/agent-memory/docs-db/agent-docs-index.db')
    
    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    
    # Create tables
    with open('/app/src/schema/docs_db_schema.sql', 'r') as f:
        schema = f.read()
        conn.executescript(schema)
    
    # Create indexes
    with open('/app/src/schema/docs_db_indexes.sql', 'r') as f:
        indexes = f.read()
        conn.executescript(indexes)
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized at {db_path}")

if __name__ == '__main__':
    init_database()
```

### Backup and Recovery
```python
# scripts/backup_docs_db.py
import sqlite3
import shutil
import os
from datetime import datetime

def backup_database():
    """Create a backup of the documentation database."""
    db_path = os.getenv('DOCS_DB_PATH', '/app/agent-memory/docs-db/agent-docs-index.db')
    backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    
    # Ensure backup directory exists
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'agent-docs-index_{timestamp}.db')
    
    # Create backup
    shutil.copy2(db_path, backup_path)
    
    # Clean old backups (keep last 10)
    backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')])
    if len(backups) > 10:
        for old_backup in backups[:-10]:
            os.remove(os.path.join(backup_dir, old_backup))
    
    print(f"Database backed up to {backup_path}")

if __name__ == '__main__':
    backup_database()
```

---

## Implementation Roadmap

### Phase 1: Foundation (Sprint 2.7)
- [ ] Database schema implementation
- [ ] Basic document indexing
- [ ] Simple search functionality
- [ ] Docker volume configuration
- [ ] Integration with existing workflows

### Phase 2: Enhanced Search (Sprint 2.8)
- [ ] Semantic search implementation
- [ ] Embedding generation and storage
- [ ] Advanced query capabilities
- [ ] Relationship mapping

### Phase 3: Analytics and Visualization (Sprint 2.9)
- [ ] Analytics dashboard
- [ ] Coverage reporting
- [ ] Quality metrics
- [ ] Usage tracking

### Phase 4: Advanced Features (Sprint 3.0)
- [ ] Knowledge graph visualization
- [ ] Automated gap detection
- [ ] Integration with external tools
- [ ] Advanced analytics

---

## Success Metrics

### Technical Metrics
- **Search Performance:** Query response time < 100ms
- **Indexing Speed:** Document indexing < 1 second per document
- **Storage Efficiency:** Metadata size < 10% of original content
- **Availability:** Database uptime > 99.9%

### User Experience Metrics
- **Search Accuracy:** Relevant results in top 5 > 90%
- **Discovery Rate:** New documentation discovered > 50%
- **Usage Increase:** Documentation usage increase > 25%
- **User Satisfaction:** User satisfaction score > 4.5/5

### Business Metrics
- **Productivity:** Time saved in documentation search > 30%
- **Quality:** Documentation quality improvement > 20%
- **Coverage:** Documentation coverage increase > 15%
- **Maintenance:** Documentation maintenance effort reduction > 25%

---

**Status:** Paper architecture complete - ready for implementation after repository restructure. 