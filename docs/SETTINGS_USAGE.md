# Using Settings in Your Code

## Quick Start

Import and use settings throughout your application:

```python
from app.settings import settings

# Access configuration
database_url = settings.database_url
embedding_key = settings.embedding_key
chunk_size = settings.rag_chunk_size
```

## Examples

### In a Module

```python
# app/my_module.py
from app.settings import settings

def connect_to_database():
    # Use the normalized database URL
    url = settings.database_url_normalized
    # ... connect
```

### In FastAPI Dependency

```python
from fastapi import Depends
from app.settings import settings

def get_settings():
    return settings

@app.get("/config")
def show_config(config: Settings = Depends(get_settings)):
    return {
        "environment": config.app_env,
        "log_level": config.log_level
    }
```

### Accessing Computed Properties

```python
from app.settings import settings

# Get embedding API base with /v1 suffix
api_base = settings.embedding_api_base
# Returns: "https://ai.heroku.com/embeddings/v1"

# Get normalized database URL (postgres:// → postgresql://)
db_url = settings.database_url_normalized
```

## Benefits

1. **Type Safety**: Autocomplete and type checking in your IDE
2. **Single Source of Truth**: All config in one place
3. **Validation**: Errors on startup if config is invalid
4. **Testability**: Easy to override settings in tests
5. **Documentation**: Settings are self-documenting with descriptions

## Testing

Override settings in tests:

```python
from app.settings import Settings

def test_with_custom_settings(monkeypatch):
    # Override environment variables
    monkeypatch.setenv("RAG_CHUNK_SIZE", "256")
    
    # Reload settings
    test_settings = Settings()
    
    assert test_settings.rag_chunk_size == 256
```

## Migration from os.environ

**Before:**
```python
import os
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL not set")
```

**After:**
```python
from app.settings import settings
database_url = settings.database_url  # Validated on startup
```

The settings system validates required fields on import, so you get immediate feedback if configuration is missing.

