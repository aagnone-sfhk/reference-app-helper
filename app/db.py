"""
Database operations for the LlamaIndex RAG application.
Handles PostgreSQL operations for document storage and retrieval.
"""

from sqlalchemy import create_engine, text
from .settings import settings


def get_db_engine():
    """Get database engine for PostgreSQL operations"""
    try:
        # Get normalized database URL from settings
        database_url = settings.database_url_normalized

        # Create and return engine
        return create_engine(database_url)

    except Exception as e:
        raise Exception(f"Failed to create database engine: {str(e)}")


def clear_vector_database():
    """Clear all documents from the PostgreSQL vector database table"""
    try:
        engine = get_db_engine()

        with engine.connect() as connection:
            # Clear the documents table (this is the table name used in PGVectorStore)
            connection.execute(text("DELETE FROM documents"))
            connection.commit()

        return True, "Successfully cleared vector database"

    except Exception as e:
        return False, f"Error clearing vector database: {str(e)}"


def get_database_document_count():
    """Get the number of documents stored in the PostgreSQL vector database"""
    try:
        engine = get_db_engine()

        with engine.connect() as connection:
            # Count documents in the documents table
            result = connection.execute(
                text("SELECT COUNT(*) FROM documents"))
            count = result.scalar()

        return count, "Success"

    except Exception as e:
        return None, f"Error querying database: {str(e)}"


def delete_document_from_index(filename):
    """Delete all document chunks from the vector database for a specific filename"""
    try:
        engine = get_db_engine()

        with engine.connect() as connection:
            # Delete all rows where the metadata contains the specific filename
            result = connection.execute(
                text(
                    "DELETE FROM documents WHERE metadata_->>'file_name' = :filename"),
                {"filename": filename}
            )
            deleted_count = result.rowcount
            connection.commit()

        return True, f"Successfully deleted {deleted_count} chunk(s) for {filename} from vector database"

    except Exception as e:
        return False, f"Error deleting {filename} from vector database: {str(e)}"

