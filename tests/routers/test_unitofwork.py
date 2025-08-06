import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
import heroku_applink as sdk

@pytest.mark.asyncio
async def test_create_unit_of_work(client):
    """
    Test the /unitofwork endpoint.
    """
    context = sdk.get_client_context()
    data_api = context.org.data_api
    
    mock_uow = MagicMock()
    # THIS IS THE FIX:
    # We replace the default async method with a synchronous MagicMock
    # to correctly mimic the real SDK's behavior.
    data_api.new_unit_of_work = MagicMock(return_value=mock_uow)
    
    commit_result = MagicMock()
    commit_result.get.side_effect = [
        MagicMock(id="acc1"), MagicMock(id="con1"),
        MagicMock(id="case1"), MagicMock(id="case2"),
    ]
    data_api.commit_unit_of_work.return_value = commit_result

    request_data = {
        "data": {
            "accountName": "Test Account", "lastName": "Test",
            "subject": "Test Case", "callbackUrl": "http://localhost/callback"
        }
    }

    response = client.post("/unitofwork/", json=request_data)

    assert response.status_code == 201
    assert response.json() == {"success": True}
    data_api.new_unit_of_work.assert_called_once()
    data_api.commit_unit_of_work.assert_called_once_with(mock_uow)
    context.org.request.assert_called_once()

@pytest.mark.asyncio
async def test_create_unit_of_work_no_callback(client):
    """
    Test the /unitofwork endpoint when no callbackUrl is provided.
    """
    context = sdk.get_client_context()
    data_api = context.org.data_api
    
    mock_uow = MagicMock()
    data_api.new_unit_of_work = MagicMock(return_value=mock_uow)
    
    commit_result = MagicMock()
    commit_result.get.side_effect = [
        MagicMock(id="acc1"), MagicMock(id="con1"),
        MagicMock(id="case1"), MagicMock(id="case2"),
    ]
    data_api.commit_unit_of_work.return_value = commit_result

    request_data = {
        "data": {
            "accountName": "Test Account", "lastName": "Test",
            "subject": "Test Case"
        }
    }

    response = client.post("/unitofwork/", json=request_data)

    assert response.status_code == 201
    assert response.json() == {"success": True}
    context.org.request.assert_not_called()

@pytest.mark.asyncio
async def test_create_unit_of_work_commit_fails(client):
    """
    Test the /unitofwork endpoint when the commit fails.
    """
    context = sdk.get_client_context()
    data_api = context.org.data_api
    
    mock_uow = MagicMock()
    data_api.new_unit_of_work = MagicMock(return_value=mock_uow)
    
    data_api.commit_unit_of_work.side_effect = Exception("Commit failed!")

    request_data = {
        "data": {
            "accountName": "Test Account", "lastName": "Test",
            "subject": "Test Case"
        }
    }

    # The TestClient will not re-raise the HTTPException.
    # Instead, it will return a Response object with the 500 status code.
    response = client.post("/unitofwork/", json=request_data)

    assert response.status_code == 500
    assert "Commit failed!" in response.json()["detail"]
        
    context.logger.error.assert_called_once()
