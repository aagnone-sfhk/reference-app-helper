"""
RAG (Retrieval-Augmented Generation) module for document search and question answering.

This module provides functionality to query documents stored in a PostgreSQL vector
database using LlamaIndex and Heroku AI models.
"""

from typing import Optional
from llama_index.llms.heroku import Heroku
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy import make_url

from .settings import settings


def create_embedding_model() -> OpenAILikeEmbedding:
    """
    Create and configure the embedding model for vector operations.
    
    Returns:
        Configured OpenAILikeEmbedding instance
    """
    return OpenAILikeEmbedding(
        api_base=settings.embedding_api_base,
        api_key=settings.embedding_key,
        model_name=settings.embedding_model_id,
        embed_batch_size=settings.rag_embed_batch_size,
    )


def create_text_splitter() -> SentenceSplitter:
    """
    Create and configure the text splitter for document chunking.
    
    Returns:
        Configured SentenceSplitter instance
    """
    return SentenceSplitter(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        separator=" ",
    )


def create_vector_store() -> PGVectorStore:
    """
    Create and configure the PostgreSQL vector store.
    
    Returns:
        Configured PGVectorStore instance connected to the database
    """
    url = make_url(settings.database_url_normalized)
    
    return PGVectorStore.from_params(
        database=url.database,
        host=url.host,
        port=url.port,
        user=url.username,
        password=url.password,
        table_name="documents",
        embed_dim=settings.rag_embed_dim,
        hnsw_kwargs={
            "hnsw_m": 16,
            "hnsw_ef_construction": 64,
            "hnsw_ef_search": 40,
            "hnsw_dist_method": "vector_cosine_ops",
        },
    )


def configure_llama_index():
    """
    Configure global LlamaIndex settings with the application's LLM and embedding models.
    
    This should be called once during application startup or before creating a query engine.
    """
    Settings.llm = Heroku()
    Settings.embed_model = create_embedding_model()
    Settings.text_splitter = create_text_splitter()


def create_query_engine(
    response_mode: str = "tree_summarize",
    top_k: int = 10
):
    """
    Create a query engine for searching and answering questions from documents.
    
    This function loads the existing vector index from PostgreSQL and creates
    a query engine configured for the specified retrieval parameters.
    
    Args:
        response_mode: How to combine retrieved chunks into a response.
            Options: "tree_summarize" (default), "refine", "compact", "simple_summarize"
        top_k: Number of most relevant document chunks to retrieve (default: 10)
    
    Returns:
        A configured query engine ready to answer questions
    
    Example:
        >>> engine = create_query_engine(response_mode="tree_summarize", top_k=10)
        >>> response = query(engine, "What is machine learning?")
    """
    # Configure global settings
    configure_llama_index()
    
    # Create vector store connection
    vector_store = create_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Load the existing index from the database
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=Settings.embed_model,
        storage_context=storage_context,
    )
    
    # Create and configure the query engine
    query_engine = index.as_query_engine(
        llm=Settings.llm,
        response_mode=response_mode,
        similarity_top_k=top_k,
    )
    
    return query_engine


def query(query_engine, prompt: str) -> tuple[str, list[dict]]:
    """
    Execute a query against the document index.
    
    Args:
        query_engine: A query engine created by create_query_engine()
        prompt: The question or query to answer
    
    Returns:
        Tuple of (generated answer, list of source metadata dicts)
    
    Example:
        >>> engine = create_query_engine()
        >>> answer, sources = query(engine, "What is the main topic of the documents?")
        >>> print(answer)
        >>> print(sources)
    """
    response = query_engine.query(prompt)
    
    # Extract metadata from source nodes
    sources = []
    if hasattr(response, 'source_nodes'):
        for node in response.source_nodes:
            source_info = {
                "text": node.text[:200] + "..." if len(node.text) > 200 else node.text,
                "score": float(node.score) if hasattr(node, 'score') else None,
                "metadata": node.metadata if hasattr(node, 'metadata') else {}
            }
            sources.append(source_info)
    
    return str(response), sources

