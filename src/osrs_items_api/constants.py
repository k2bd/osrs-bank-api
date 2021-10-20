import os
from typing import Optional

#: Name of the item tags table in DynamoDB
TAGS_TABLE_NAME: str = os.environ["OSRS_TAGS_TABLE_NAME"]

#: Name of the item tags table in DynamoDB
TAG_GROUPS_TABLE_NAME: str = os.environ["OSRS_TAG_GROUPS_TABLE_NAME"]

#: Name of the bank tags index of the item tags table in DynamoDB
BANK_TAGS_INDEX_NAME: str = "bank-tags"

#: AWS region for connecting to AWS resources
AWS_REGION: Optional[str] = os.environ.get("AWS_REGION")

#: Optional endpoint for a local DynamoDB instance, taking precedence over AWS_REGION
LOCAL_DYNAMODB_ENDPOINT: Optional[str] = os.environ.get("LOCAL_DYNAMODB_ENDPOINT")
