import boto3
import pytest
from fastapi.testclient import TestClient

from osrs_items_api._tablespec import tags_table, tag_groups_table
from osrs_items_api.api import app
from osrs_items_api.constants import LOCAL_DYNAMODB_ENDPOINT, TAG_GROUPS_TABLE_NAME, TAGS_TABLE_NAME
from osrs_items_api.tags_service import TagsService


@pytest.fixture
def dynamodb_client():
    assert LOCAL_DYNAMODB_ENDPOINT is not None
    return boto3.client("dynamodb", endpoint_url=LOCAL_DYNAMODB_ENDPOINT)


@pytest.fixture
def temporary_tags_table(dynamodb_client):
    """
    Create a temporary clean tags table, tearing it down after the test.
    Uses waiters to ensure the table is properly created and destroyed before
    moving on.
    """
    table = dynamodb_client.create_table(**tags_table)

    exists_waiter = dynamodb_client.get_waiter("table_exists")
    not_exists_waiter = dynamodb_client.get_waiter("table_not_exists")

    exists_waiter.wait(TableName=TAGS_TABLE_NAME)

    try:
        yield table
    finally:
        dynamodb_client.delete_table(TableName=TAGS_TABLE_NAME)
        not_exists_waiter.wait(TableName=TAGS_TABLE_NAME)


@pytest.fixture
def temporary_tag_groups_table(dynamodb_client):
    """
    Create a temporary clean tag groups table, tearing it down after the test.
    Uses waiters to ensure the table is properly created and destroyed before
    moving on.
    """
    table = dynamodb_client.create_table(**tag_groups_table)

    exists_waiter = dynamodb_client.get_waiter("table_exists")
    not_exists_waiter = dynamodb_client.get_waiter("table_not_exists")

    exists_waiter.wait(TableName=TAG_GROUPS_TABLE_NAME)

    try:
        yield table
    finally:
        dynamodb_client.delete_table(TableName=TAG_GROUPS_TABLE_NAME)
        not_exists_waiter.wait(TableName=TAG_GROUPS_TABLE_NAME)


@pytest.fixture
def tags_service(temporary_tags_table, temporary_tag_groups_table) -> TagsService:
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
