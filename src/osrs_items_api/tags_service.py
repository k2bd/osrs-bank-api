from typing import List, Optional

from boto3.dynamodb.conditions import Key

from osrs_items_api.constants import BANK_TAGS_INDEX_NAME, TAGS_TABLE_NAME
from osrs_items_api.dynamodb import dynamodb
from osrs_items_api.types import Item, Tag


class TagsService:
    def __init__(self):
        self.db = dynamodb()
        self.tags_table = self.db.Table(TAGS_TABLE_NAME)

    def add_tag(self, item_id: int, tag_name: str) -> Tag:
        """
        Idempotently add a new tag to an item
        """
        tag = Tag(
            item_id=item_id,
            tag_name=tag_name,
        )
        self.tags_table.put_item(Item=(tag.dict()))

        return tag

    def get_tag(
        self, item_id: int, tag_name: str, consistent_read=False
    ) -> Optional[Tag]:
        """
        Get a tag if it exists, or None if it doesn't exist
        """
        response = self.tags_table.get_item(
            Key=dict(
                item_id=item_id,
                tag_name=tag_name,
            ),
            ConsistentRead=consistent_read,
        )

        if "Item" not in response:
            return None

        return Tag.parse_obj(response["Item"])

    def delete_tag(self, item_id: int, tag_name: str) -> Tag:
        """
        Idempotently remove a tag from an item
        """
        tag = Tag(
            item_id=item_id,
            tag_name=tag_name,
        )
        self.tags_table.delete_item(
            Key=dict(
                item_id=item_id,
                tag_name=tag_name,
            )
        )
        return tag

    def get_item_tags(self, item: Item) -> List[Tag]:
        """
        Get all tags of a given item
        """
        # TODO: paginate and lazily yield from pages
        result = self.tags_table.query(
            KeyConditionExpression=Key("item_id").eq(item.item_id)
        )

        if "Items" not in result:
            return []

        return [Tag.parse_obj(result) for result in result["Items"]]

    def get_bank_tags(self, tag_name: str) -> List[Tag]:
        """
        Get all tags with a given name
        """
        # TODO: paginate and yield from pages
        result = self.tags_table.query(
            IndexName=BANK_TAGS_INDEX_NAME,
            KeyConditionExpression=Key("tag_name").eq(tag_name),
        )

        if "Items" not in result:
            return []

        return [Tag.parse_obj(result) for result in result["Items"]]
