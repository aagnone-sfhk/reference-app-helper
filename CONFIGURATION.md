# Configuration Guide

This application uses `pydantic-settings` for type-safe environment variable management.

## Environment Variables

All configuration is managed through environment variables. You can set these in:
- Environment variables directly
- A `.env` file in the project root

### Required Variables

#### Database
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```
PostgreSQL database URL with pgvector support. The app automatically converts `postgres://` to `postgresql://` for SQLAlchemy compatibility.

#### Heroku AI - Inference
```bash
INFERENCE_URL=https://ai.heroku.com/inference
INFERENCE_KEY=your-inference-api-key
INFERENCE_MODEL_ID=your-inference-model-id
```
Heroku AI configuration for LLM inference. The URL defaults to `https://ai.heroku.com/inference` if not set.

#### Heroku AI - Embeddings
```bash
EMBEDDING_URL=https://ai.heroku.com/embeddings
EMBEDDING_KEY=your-embedding-api-key
EMBEDDING_MODEL_ID=cohere-embed-multilingual
```
Heroku AI configuration for embeddings. The URL defaults to `https://ai.heroku.com/embeddings` if not set.

### Optional Variables (with defaults)

#### RAG Configuration
```bash
RAG_CHUNK_SIZE=512              # Max characters per document chunk
RAG_CHUNK_OVERLAP=10            # Overlap between chunks for context
RAG_EMBED_BATCH_SIZE=96         # Batch size for embedding operations
RAG_EMBED_DIM=1024              # Embedding dimension (1024 for Cohere)
```

#### Application Configuration
```bash
APP_ENV=development             # Application environment
LOG_LEVEL=INFO                  # Logging level
```

## Settings Module

The settings are defined in `app/settings.py` using Pydantic Settings:

```python
from app.settings import settings

# Access settings
database_url = settings.database_url_normalized
embedding_key = settings.embedding_key
```

### Key Features

1. **Type Safety**: All settings have proper type annotations
2. **Validation**: Pydantic validates types and required fields
3. **Defaults**: Sensible defaults for optional settings
4. **Case Insensitive**: Environment variables are case-insensitive
5. **Auto .env Loading**: Automatically loads from `.env` file

### Properties

The settings object provides computed properties:

- `database_url_normalized`: Converts `postgres://` to `postgresql://`
- `embedding_api_base`: Adds `/v1` suffix for OpenAI-like client

## Getting Heroku Config

To populate your `.env` file from Heroku:

```bash
heroku config -s > .env
```

This will export all Heroku config vars in the correct format.

## Example .env File

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Heroku AI - Inference
INFERENCE_URL=https://ai.heroku.com/inference
INFERENCE_KEY=your-inference-api-key
INFERENCE_MODEL_ID=meta-llama/Meta-Llama-3.1-70B-Instruct

# Heroku AI - Embeddings
EMBEDDING_URL=https://ai.heroku.com/embeddings
EMBEDDING_KEY=your-embedding-api-key
EMBEDDING_MODEL_ID=cohere-embed-multilingual

# Optional: RAG Configuration
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=10
RAG_EMBED_BATCH_SIZE=96
RAG_EMBED_DIM=1024

# Optional: Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
```

## Troubleshooting

### Missing Required Variables

If required environment variables are missing, you'll see a Pydantic validation error:

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
database_url
  Field required [type=missing, input_value={...}, input_type=dict]
```

Solution: Ensure all required variables are set in your environment or `.env` file.

### Invalid Values

If a value doesn't match the expected type:

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
rag_chunk_size
  Input should be a valid integer [type=int_type, input_value='abc', input_type=str]
```

Solution: Verify the value matches the expected type (int, str, etc.).

