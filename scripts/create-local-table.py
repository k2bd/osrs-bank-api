import boto3

from osrs_items_api._tablespec import tag_groups_table, tags_table
from osrs_items_api.constants import (
    LOCAL_DYNAMODB_ENDPOINT,
    TAG_GROUPS_TABLE_NAME,
    TAGS_TABLE_NAME,
)


def make_tags_table():
    """
    Create a temporary clean tags table, tearing it down after the test.
    Uses waiters to ensure the table is properly created and destroyed before
    moving on.
    """
    if not LOCAL_DYNAMODB_ENDPOINT:
        raise EnvironmentError("Please set LOCAL_DYNAMODB_ENDPOINT")

    dynamodb_client = boto3.client("dynamodb", endpoint_url=LOCAL_DYNAMODB_ENDPOINT)

    try:
        dynamodb_client.create_table(**tags_table)
    except dynamodb_client.exceptions.ResourceInUseException:
        print("Using existing tags table")
        return

    exists_waiter = dynamodb_client.get_waiter("table_exists")
    exists_waiter.wait(TableName=TAGS_TABLE_NAME)


def make_tag_groups_table():
    """
    Create a temporary clean tags table, tearing it down after the test.
    Uses waiters to ensure the table is properly created and destroyed before
    moving on.
    """
    if not LOCAL_DYNAMODB_ENDPOINT:
        raise EnvironmentError("Please set LOCAL_DYNAMODB_ENDPOINT")

    dynamodb_client = boto3.client("dynamodb", endpoint_url=LOCAL_DYNAMODB_ENDPOINT)

    try:
        dynamodb_client.create_table(**tag_groups_table)
    except dynamodb_client.exceptions.ResourceInUseException:
        print("Using existing tag groups table")
        return

    exists_waiter = dynamodb_client.get_waiter("table_exists")
    exists_waiter.wait(TableName=TAG_GROUPS_TABLE_NAME)


if __name__ == "__main__":
    make_tags_table()
    make_tag_groups_table()
