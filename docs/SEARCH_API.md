# Search API Documentation

## Overview

The `/search` endpoint provides RAG (Retrieval-Augmented Generation) capabilities for querying documents stored in a PostgreSQL vector database using LlamaIndex and Heroku AI.

## Endpoints

### GET /search

Search indexed documents using query parameters.

**Parameters:**
- `query` (required): The search query or question
- `top_k` (optional, default: 10): Number of relevant document chunks to retrieve (1-20)
- `response_mode` (optional, default: "tree_summarize"): How to combine chunks
  - `tree_summarize`: Build a tree of summaries (best for comprehensive answers)
  - `refine`: Iteratively refine the answer
  - `compact`: Combine chunks into larger context
  - `simple_summarize`: Simple concatenation

**Example:**
```bash
curl "http://localhost:8000/search?query=What%20are%20the%20benefits%20of%20AI&top_k=10&response_mode=tree_summarize"
```

**Response:**
```json
{
  "query": "What are the benefits of AI?",
  "response": "Based on the indexed documents...",
  "documents_count": 150
}
```

## Architecture

The search endpoint is **stateless** - a fresh query engine is created for each request. This ensures:
- Latest documents are always searched
- No stale cache issues
- Simple, predictable behavior
- Per-request parameter customization

## Setup Requirements

### Environment Variables

The following environment variables must be set:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Heroku AI - Inference
INFERENCE_MODEL_ID=your-inference-model-id
INFERENCE_URL=https://ai.heroku.com/inference
INFERENCE_KEY=your-api-key

# Heroku AI - Embeddings
EMBEDDING_MODEL_ID=your-embedding-model-id
EMBEDDING_URL=https://ai.heroku.com/embeddings
EMBEDDING_KEY=your-api-key
```

### Database Setup

The PostgreSQL database must have the `pgvector` extension installed:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The `documents` table will be created automatically by PGVectorStore when first initializing the RAG index.

## Document Indexing

Documents must be loaded into the PostgreSQL vector database through a separate ingestion process. The search endpoint queries existing documents only and does not index new files.

To add documents to the index:
1. Use a separate data ingestion script that uses LlamaIndex to load and embed documents
2. Store the embeddings in the PostgreSQL `documents` table
3. Documents are immediately searchable (no cache to clear)

## Implementation Details

### Components

1. **app/db.py**: Database operations for document storage/retrieval
2. **app/rag.py**: RAG query engine and document search functionality
3. **app/routers/search.py**: FastAPI router with search endpoints
4. **app/settings.py**: Configuration management with pydantic-settings

### Request Flow

1. Request arrives with query, top_k, and response_mode
2. Fresh query engine created from PostgreSQL vector store
3. Query embedded using Heroku AI embeddings
4. Embeddings matched against stored vectors (HNSW index)
5. Top-k chunks retrieved
6. Chunks sent to Heroku AI LLM for response generation
7. Response returned to client

**Note:** Query engine is created per-request (stateless), ensuring latest documents are always searched.

## Error Handling

- **404**: No documents found in the index
- **400**: Invalid parameters (e.g., invalid response_mode)
- **500**: Server error (check logs for details)

## Testing

Visit `/docs` for interactive API documentation and testing via Swagger UI.

