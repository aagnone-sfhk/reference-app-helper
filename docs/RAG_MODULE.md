# RAG Module Documentation

The `app/rag.py` module provides RAG (Retrieval-Augmented Generation) functionality for searching and answering questions from documents stored in a PostgreSQL vector database.

## Overview

This module is **not a pipeline** - it's a collection of focused functions for:
- Creating and configuring query engines
- Managing embedding models and vector stores
- Executing queries against indexed documents

## Architecture

### Modular Design

The module is organized into small, focused functions:

```
create_embedding_model()     → Configure embeddings
create_text_splitter()       → Configure chunking
create_vector_store()        → Connect to database
configure_llama_index()      → Set global settings
create_query_engine()        → Build query engine
query()                      → Execute queries
```

### Why Not a Pipeline?

This module was restructured from a "pipeline" approach to better fit the application:
- **Separation of concerns**: Each function has a single responsibility
- **Testability**: Individual components can be tested in isolation
- **Flexibility**: Components can be reused or swapped out
- **Application-first**: Designed for FastAPI integration, not batch processing

## Public API

### `create_query_engine(response_mode, top_k)`

Create a query engine for searching documents.

**Parameters:**
- `response_mode` (str): How to combine retrieved chunks
  - `"tree_summarize"` (default): Build summary tree
  - `"refine"`: Iteratively refine answer
  - `"compact"`: Combine into larger context
  - `"simple_summarize"`: Simple concatenation
- `top_k` (int): Number of chunks to retrieve (default: 10)

**Returns:**
- Query engine ready to answer questions

**Example:**
```python
from app.rag import create_query_engine, query

# Create engine
engine = create_query_engine(
    response_mode="tree_summarize",
    top_k=10
)

# Use engine
answer = query(engine, "What is machine learning?")
print(answer)
```

### `query(query_engine, prompt)`

Execute a query against the document index.

**Parameters:**
- `query_engine`: Engine created by `create_query_engine()`
- `prompt` (str): Question or query to answer

**Returns:**
- Answer as a string

**Example:**
```python
answer = query(engine, "Explain the main concepts")
```

## Helper Functions

### `create_embedding_model()`

Creates the embedding model using configuration from `settings`.

**Returns:** `OpenAILikeEmbedding` instance

### `create_text_splitter()`

Creates the text splitter for document chunking.

**Returns:** `SentenceSplitter` instance

### `create_vector_store()`

Creates PostgreSQL vector store connection.

**Returns:** `PGVectorStore` instance

**Configuration:**
- Uses HNSW indexing for fast similarity search
- Cosine distance metric
- Configurable via `settings`

### `configure_llama_index()`

Configures global LlamaIndex settings.

**Side effects:**
- Sets `Settings.llm` (Heroku AI model)
- Sets `Settings.embed_model` (embedding model)
- Sets `Settings.text_splitter` (chunking config)

## Configuration

All configuration is managed through `app/settings.py`:

```python
from app.settings import settings

# Used by the RAG module
settings.embedding_api_base      # Heroku AI embeddings endpoint
settings.embedding_key           # API key
settings.embedding_model_id      # Model ID
settings.rag_chunk_size          # Chunk size (default: 512)
settings.rag_chunk_overlap       # Overlap (default: 10)
settings.rag_embed_batch_size    # Batch size (default: 96)
settings.rag_embed_dim           # Dimensions (default: 1024)
settings.database_url_normalized # PostgreSQL URL
```

See `docs/CONFIGURATION.md` for details.

## Usage in FastAPI

The search router uses this module:

```python
# app/routers/search.py
from ..rag import create_query_engine, query

# Create engine once on first request
_query_engine = None

def initialize_rag_engine(top_k=10, response_mode="tree_summarize"):
    global _query_engine
    _query_engine = create_query_engine(
        response_mode=response_mode,
        top_k=top_k
    )

# Use engine for queries
async def search_documents(query_text: str, ...):
    if not _query_engine:
        initialize_rag_engine()
    
    answer = query(_query_engine, query_text)
    return {"query": query_text, "response": answer}
```

## Vector Store Configuration

The module uses HNSW (Hierarchical Navigable Small World) indexing:

```python
hnsw_kwargs = {
    "hnsw_m": 16,                          # Max connections per layer
    "hnsw_ef_construction": 64,            # Construction quality
    "hnsw_ef_search": 40,                  # Search quality
    "hnsw_dist_method": "vector_cosine_ops", # Distance metric
}
```

**Trade-offs:**
- Higher `hnsw_m`: More memory, faster search
- Higher `ef_construction`: Slower indexing, better quality
- Higher `ef_search`: Slower search, better recall

## Testing

Test individual components:

```python
def test_create_embedding_model():
    model = create_embedding_model()
    assert model is not None
    assert model.model_name == settings.embedding_model_id

def test_create_vector_store():
    store = create_vector_store()
    assert store is not None
    # Test connection...
```

Mock for integration tests:

```python
from unittest.mock import Mock

def test_query_with_mock_engine():
    mock_engine = Mock()
    mock_engine.query.return_value = Mock(response="Test answer")
    
    result = query(mock_engine, "Test question")
    assert result == "Test answer"
```

## Troubleshooting

### "No documents found"

The vector store is empty. Load documents via separate ingestion process.

### "Connection failed"

Check `DATABASE_URL` in settings and ensure pgvector extension is installed:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### "Invalid embedding dimensions"

Ensure `settings.rag_embed_dim` matches your embedding model (1024 for Cohere).

### Performance issues

- Reduce `top_k` for faster queries
- Use `"compact"` response mode for speed
- Adjust HNSW parameters for your use case

## Future Improvements

Potential enhancements:
- [ ] Add caching for frequently asked questions
- [ ] Support multiple indexes/collections
- [ ] Add hybrid search (keyword + semantic)
- [ ] Implement query rewriting
- [ ] Add relevance feedback

