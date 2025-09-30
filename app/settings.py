"""
Application settings and environment variable configuration.
Uses pydantic-settings for type-safe environment variable parsing.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    The settings automatically load from:
    1. Environment variables
    2. .env file (if present)
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra environment variables
    )
    
    # Database Configuration
    database_url: str = Field(
        ...,
        description="PostgreSQL database URL with pgvector support"
    )
    
    # Heroku AI - Inference Configuration
    inference_url: str = Field(
        default="https://ai.heroku.com/inference",
        description="Heroku AI inference endpoint URL"
    )
    inference_key: str = Field(
        ...,
        description="Heroku AI inference API key"
    )
    inference_model_id: str = Field(
        ...,
        description="Heroku AI inference model ID"
    )
    
    # Heroku AI - Embeddings Configuration
    embedding_url: str = Field(
        default="https://ai.heroku.com/embeddings",
        description="Heroku AI embeddings endpoint URL"
    )
    embedding_key: str = Field(
        ...,
        description="Heroku AI embeddings API key"
    )
    embedding_model_id: str = Field(
        ...,
        description="Heroku AI embeddings model ID (e.g., cohere-embed-multilingual)"
    )
    
    # RAG Configuration
    rag_chunk_size: int = Field(
        default=512,
        description="Maximum characters per document chunk"
    )
    rag_chunk_overlap: int = Field(
        default=10,
        description="Overlap between chunks for context"
    )
    rag_embed_batch_size: int = Field(
        default=96,
        description="Batch size for embedding operations"
    )
    rag_embed_dim: int = Field(
        default=1024,
        description="Embedding dimension (1024 for Cohere)"
    )
    
    # Application Configuration
    app_env: str = Field(
        default="development",
        description="Application environment (development, production, etc.)"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    @property
    def database_url_normalized(self) -> str:
        """
        Get database URL normalized for SQLAlchemy.
        Converts postgres:// to postgresql:// if needed.
        """
        return self.database_url.replace("postgres://", "postgresql://")
    
    @property
    def embedding_api_base(self) -> str:
        """Get embedding API base URL with /v1 suffix for OpenAI-like client."""
        return f"{self.embedding_url}/v1"


# Create a global settings instance
# This will be imported and used throughout the application
settings = Settings()

