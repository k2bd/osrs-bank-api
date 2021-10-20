from osrs_items_api.constants import BANK_TAGS_INDEX_NAME, TAG_GROUPS_TABLE_NAME, TAGS_TABLE_NAME

#: In-code source for the dynamodb table spec, for testing and
#: local scripts etc.
tags_table = dict(
    TableName=TAGS_TABLE_NAME,
    KeySchema=[
        {
            "AttributeName": "item_id",
            "KeyType": "HASH",
        },
        {
            "AttributeName": "group_name",
            "KeyType": "RANGE",
        },
    ],
    AttributeDefinitions=[
        {
            "AttributeName": "item_id",
            "AttributeType": "N",
        },
        {
            "AttributeName": "group_name",
            "AttributeType": "S",
        },
    ],
    ProvisionedThroughput={
        "ReadCapacityUnits": 2,
        "WriteCapacityUnits": 2,
    },
    GlobalSecondaryIndexes=[
        {
            "IndexName": BANK_TAGS_INDEX_NAME,
            "KeySchema": [
                {
                    "AttributeName": "group_name",
                    "KeyType": "HASH",
                },
                {
                    "AttributeName": "item_id",
                    "KeyType": "RANGE",
                },
            ],
            "Projection": {"ProjectionType": "ALL"},
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 2,
                "WriteCapacityUnits": 2,
            },
        }
    ],
)


tag_groups_table = dict(
    TableName=TAG_GROUPS_TABLE_NAME,
    KeySchema=[
        {
            "AttributeName": "group_name",
            "KeyType": "HASH",
        },
    ],
    AttributeDefinitions=[
        {
            "AttributeName": "group_name",
            "AttributeType": "S",
        },
    ],
    ProvisionedThroughput={
        "ReadCapacityUnits": 2,
        "WriteCapacityUnits": 2,
    },
)
