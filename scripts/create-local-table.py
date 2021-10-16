import boto3

from osrs_items_api._tablespec import local_table_spec
from osrs_items_api.constants import LOCAL_DYNAMODB_ENDPOINT, TAGS_TABLE_NAME


def tags_table():
    """
    Create a temporary clean tags table, tearing it down after the test.
    Uses waiters to ensure the table is properly created and destroyed before
    moving on.
    """
    if not LOCAL_DYNAMODB_ENDPOINT:
        raise EnvironmentError("Please set LOCAL_DYNAMODB_ENDPOINT")

    dynamodb_client = boto3.client("dynamodb", endpoint_url=LOCAL_DYNAMODB_ENDPOINT)

    try:
        dynamodb_client.create_table(**local_table_spec)
    except dynamodb_client.exceptions.ResourceInUseException:
        print("Using existing tags table")
        return

    exists_waiter = dynamodb_client.get_waiter("table_exists")
    exists_waiter.wait(TableName=TAGS_TABLE_NAME)


if __name__ == "__main__":
    tags_table()
