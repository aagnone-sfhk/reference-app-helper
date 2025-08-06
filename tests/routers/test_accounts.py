import pytest
from unittest.mock import MagicMock
import heroku_applink as sdk

@pytest.mark.asyncio
async def test_get_accounts(client):
    """
    Test the /accounts endpoint.
    """
    mock_record = MagicMock()
    mock_record.fields = {"Id": "123", "Name": "Test Account"}
    
    context = sdk.get_client_context()
    context.data_api.query.return_value = MagicMock(records=[mock_record])

    response = client.get("/api/accounts/")
    
    assert response.status_code == 200
    assert response.json() == [{"id": "123", "name": "Test Account"}]
    context.data_api.query.assert_called_once_with("SELECT Id, Name FROM Account")
