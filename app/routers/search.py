"""
Search endpoint using RAG for document retrieval.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import logging

from ..rag import create_query_engine, query
from ..db import get_database_document_count

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"])


class SearchResponse(BaseModel):
    """Response model for search endpoint"""
    query: str
    response: str
    documents_count: int


@router.get("/search", response_model=SearchResponse, summary="Search documents using RAG")
async def search_documents(
    query_text: str = Query(..., description="The search query string", alias="query"),
    top_k: int = Query(
        10, description="Number of relevant document chunks to retrieve", ge=1, le=20),
    response_mode: str = Query(
        "tree_summarize",
        description="Response mode: tree_summarize, refine, compact, or simple_summarize"
    )
):
    """
    Search indexed documents using RAG (Retrieval-Augmented Generation).

    This endpoint performs semantic search over indexed documents and generates
    a response using the retrieved context.

    **Parameters:**
    - **query**: The search query or question
    - **top_k**: Number of relevant document chunks to retrieve (1-20, default: 10)
    - **response_mode**: How to combine chunks:
        - `tree_summarize`: Build a tree of summaries (default, best for comprehensive answers)
        - `refine`: Iteratively refine the answer
        - `compact`: Combine chunks into larger context
        - `simple_summarize`: Simple concatenation

    **Returns:**
    - Search query
    - Generated response based on retrieved documents
    - Number of documents in the index
    
    **Note:** Query engine is created fresh for each request, ensuring
    the latest documents are always searched.
    """
    try:
        # Validate response_mode
        valid_modes = ["tree_summarize", "refine", "compact", "simple_summarize"]
        if response_mode not in valid_modes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid response_mode. Must be one of: {', '.join(valid_modes)}"
            )

        # Get database stats
        doc_count, _ = get_database_document_count()

        # Check if we have documents to search
        if doc_count == 0:
            raise HTTPException(
                status_code=404,
                detail="No documents found in the index. Please load documents into the vector database first."
            )

        # Create query engine for this request (stateless, always up-to-date)
        logger.info(f"Creating query engine with top_k={top_k}, response_mode={response_mode}")
        engine = create_query_engine(
            response_mode=response_mode,
            top_k=top_k
        )

        # Perform the search using RAG
        logger.info(f"Querying documents with: '{query_text}'")
        answer = query(engine, query_text)

        return SearchResponse(
            query=query_text,
            response=answer,
            documents_count=doc_count if doc_count else 0
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )



