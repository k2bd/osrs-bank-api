import boto3
import pytest
from fastapi.testclient import TestClient

from osrs_items_api._tablespec import local_table_spec
from osrs_items_api.api import app
from osrs_items_api.constants import LOCAL_DYNAMODB_ENDPOINT, TAGS_TABLE_NAME
from osrs_items_api.tags_service import TagsService


@pytest.fixture
def dynamodb_client():
    assert LOCAL_DYNAMODB_ENDPOINT is not None
    return boto3.client("dynamodb", endpoint_url=LOCAL_DYNAMODB_ENDPOINT)


@pytest.fixture
def tags_table(dynamodb_client):
    """
    Create a temporary clean tags table, tearing it down after the test.
    Uses waiters to ensure the table is properly created and destroyed before
    moving on.
    """
    table = dynamodb_client.create_table(**local_table_spec)

    exists_waiter = dynamodb_client.get_waiter("table_exists")
    not_exists_waiter = dynamodb_client.get_waiter("table_not_exists")

    exists_waiter.wait(TableName=TAGS_TABLE_NAME)

    try:
        yield table
    finally:
        dynamodb_client.delete_table(TableName=TAGS_TABLE_NAME)
        not_exists_waiter.wait(TableName=TAGS_TABLE_NAME)


@pytest.fixture
def tags_service(games_table) -> TagsService:
    """
    Return a service that can interact with a temporary games table
    """
    return TagsService()


@pytest.fixture
def api_client(tags_service) -> TestClient:
    """
    Return an API test client that can interact with a temporary database
    """
    return TestClient(app)
