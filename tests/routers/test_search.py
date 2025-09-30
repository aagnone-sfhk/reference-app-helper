import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
async def test_search_documents_success(client):
    """
    Test the /search endpoint with valid query returns expected response.
    """
    # Mock the database document count
    with patch("app.routers.search.get_database_document_count") as mock_count, \
         patch("app.routers.search.create_query_engine") as mock_engine, \
         patch("app.routers.search.query") as mock_query:
        
        # Setup mocks
        mock_count.return_value = (42, 5)  # 42 documents, 5 unique sources
        mock_query_engine = MagicMock()
        mock_engine.return_value = mock_query_engine
        mock_query.return_value = "This is a test response from the RAG system."
        
        # Make request
        response = client.get("/search?query=test+question&top_k=5&response_mode=tree_summarize")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test question"
        assert data["response"] == "This is a test response from the RAG system."
        assert data["documents_count"] == 42
        
        # Verify mocks were called correctly
        mock_count.assert_called_once()
        mock_engine.assert_called_once_with(response_mode="tree_summarize", top_k=5)
        mock_query.assert_called_once_with(mock_query_engine, "test question")


@pytest.mark.asyncio
async def test_search_documents_no_documents(client):
    """
    Test the /search endpoint returns 404 when no documents are indexed.
    """
    with patch("app.routers.search.get_database_document_count") as mock_count:
        mock_count.return_value = (0, 0)
        
        response = client.get("/search?query=test")
        
        assert response.status_code == 404
        assert "No documents found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_search_documents_invalid_response_mode(client):
    """
    Test the /search endpoint rejects invalid response_mode.
    """
    with patch("app.routers.search.get_database_document_count") as mock_count:
        mock_count.return_value = (10, 2)
        
        response = client.get("/search?query=test&response_mode=invalid_mode")
        
        assert response.status_code == 400
        assert "Invalid response_mode" in response.json()["detail"]


@pytest.mark.asyncio
async def test_search_documents_missing_query(client):
    """
    Test the /search endpoint requires query parameter.
    """
    response = client.get("/search")
    
    assert response.status_code == 422  # FastAPI validation error


@pytest.mark.asyncio
async def test_search_documents_default_parameters(client):
    """
    Test the /search endpoint uses correct defaults when parameters not provided.
    """
    with patch("app.routers.search.get_database_document_count") as mock_count, \
         patch("app.routers.search.create_query_engine") as mock_engine, \
         patch("app.routers.search.query") as mock_query:
        
        mock_count.return_value = (100, 10)
        mock_query_engine = MagicMock()
        mock_engine.return_value = mock_query_engine
        mock_query.return_value = "Default response"
        
        response = client.get("/search?query=test")
        
        assert response.status_code == 200
        # Verify defaults: top_k=10, response_mode="tree_summarize"
        mock_engine.assert_called_once_with(response_mode="tree_summarize", top_k=10)


@pytest.mark.asyncio
async def test_search_documents_top_k_bounds(client):
    """
    Test the /search endpoint validates top_k parameter bounds.
    """
    with patch("app.routers.search.get_database_document_count") as mock_count:
        mock_count.return_value = (10, 2)
        
        # Test top_k too low
        response = client.get("/search?query=test&top_k=0")
        assert response.status_code == 422
        
        # Test top_k too high
        response = client.get("/search?query=test&top_k=21")
        assert response.status_code == 422
        
        # Test top_k at boundaries (should succeed)
        with patch("app.routers.search.create_query_engine") as mock_engine, \
             patch("app.routers.search.query") as mock_query:
            mock_query_engine = MagicMock()
            mock_engine.return_value = mock_query_engine
            mock_query.return_value = "Response"
            
            response = client.get("/search?query=test&top_k=1")
            assert response.status_code == 200
            
            response = client.get("/search?query=test&top_k=20")
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_documents_handles_query_error(client):
    """
    Test the /search endpoint handles errors gracefully.
    """
    with patch("app.routers.search.get_database_document_count") as mock_count, \
         patch("app.routers.search.create_query_engine") as mock_engine:
        
        mock_count.return_value = (10, 2)
        mock_engine.side_effect = Exception("Database connection failed")
        
        response = client.get("/search?query=test")
        
        assert response.status_code == 500
        assert "Search failed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_search_documents_all_response_modes(client):
    """
    Test the /search endpoint accepts all valid response modes.
    """
    valid_modes = ["tree_summarize", "refine", "compact", "simple_summarize"]
    
    for mode in valid_modes:
        with patch("app.routers.search.get_database_document_count") as mock_count, \
             patch("app.routers.search.create_query_engine") as mock_engine, \
             patch("app.routers.search.query") as mock_query:
            
            mock_count.return_value = (10, 2)
            mock_query_engine = MagicMock()
            mock_engine.return_value = mock_query_engine
            mock_query.return_value = f"Response with {mode}"
            
            response = client.get(f"/search?query=test&response_mode={mode}")
            
            assert response.status_code == 200, f"Failed for mode: {mode}"
            mock_engine.assert_called_once_with(response_mode=mode, top_k=10)

