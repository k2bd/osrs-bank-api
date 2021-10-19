from osrs_items_api.constants import BANK_TAGS_INDEX_NAME, TAGS_TABLE_NAME

#: In-code source for the dynamodb table spec, for testing and
#: local scripts etc.
local_table_spec = dict(
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
    BillingMode="PAY_PER_REQUEST",
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
            "BillingMode": "PAY_PER_REQUEST",
        }
    ],
)
