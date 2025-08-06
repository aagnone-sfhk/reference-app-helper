import pytest
from unittest.mock import MagicMock
import heroku_applink as sdk

# This is a complete, valid payload that matches the Pydantic model
VALID_REQUEST_DATA = {
    "events": [
        {
            "ActionDeveloperName": "test",
            "EventType": "test",
            "EventPrompt": "test",
            "SourceObjectDeveloperName": "test",
            "EventPublishDateTime": "2024-01-01T12:00:00Z",
            "PayloadCurrentValue": {"key": "value"},
        }
    ],
    "schemas": [{"schemaId": "test_schema"}],
}


@pytest.mark.asyncio
async def test_handle_data_cloud_change_event(client):
    """
    Test the /handleDataCloudDataChangeEvent endpoint.
    """
    context = sdk.get_client_context()
    data_cloud = context.data_cloud

    mock_event = MagicMock(count=1, schemas=[], events=[MagicMock()])
    data_cloud.parse_data_action_event.return_value = mock_event

    response = client.post("/handleDataCloudDataChangeEvent/", json=VALID_REQUEST_DATA)

    assert response.status_code == 204
    data_cloud.parse_data_action_event.assert_called_once_with(VALID_REQUEST_DATA)


@pytest.mark.asyncio
async def test_handle_data_cloud_change_event_with_query(client, monkeypatch):
    """
    Test the /handleDataCloudDataChangeEvent endpoint when env vars are set.
    """
    monkeypatch.setenv("DATA_CLOUD_ORG", "my-dc-org")
    monkeypatch.setenv("DATA_CLOUD_QUERY", "SELECT Id FROM SomeObject")

    context = sdk.get_client_context()
    data_cloud = context.data_cloud
    app_link_addon = context.addons.applink

    mock_event = MagicMock(count=1, schemas=[], events=[MagicMock()])
    data_cloud.parse_data_action_event.return_value = mock_event

    response = client.post("/handleDataCloudDataChangeEvent/", json=VALID_REQUEST_DATA)

    assert response.status_code == 204
    app_link_addon.get_authorization.assert_called_once_with("my-dc-org")
    mock_org = await app_link_addon.get_authorization()
    mock_org.data_cloud_api.query.assert_called_once_with("SELECT Id FROM SomeObject")
