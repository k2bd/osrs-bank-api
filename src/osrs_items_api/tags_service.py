from typing import List, Optional

from boto3.dynamodb.conditions import Key

from osrs_items_api.constants import (
    BANK_TAGS_INDEX_NAME,
    TAG_GROUPS_TABLE_NAME,
    TAGS_TABLE_NAME,
)
from osrs_items_api.dynamodb import dynamodb
from osrs_items_api.logging import get_logger
from osrs_items_api.types import Item, Tag, TagGroup

logger = get_logger()


# TODO: async service
class TagsService:
    def __init__(self):
        self.db = dynamodb()
        self.tags_table = self.db.Table(TAGS_TABLE_NAME)
        self.tag_groups_table = self.db.Table(TAG_GROUPS_TABLE_NAME)

    def add_tag(self, tag: Tag) -> Tag:
        """
        Idempotently add a new tag to an item, also creating a tag group if it doesn't
        already exist.
        """
        logger.info("Creating %s", tag)
        self.tags_table.put_item(Item=tag.dict())

        if not self.get_tag_group(tag.group_name):
            logger.info("Also creating a new tag group for %s", tag.group_name)
            self.add_tag_group(TagGroup(group_name=tag.group_name))

        return tag

    def get_tag(self, tag: Tag, consistent_read=False) -> Optional[Tag]:
        """
        Get a tag if it exists, or None if it doesn't exist
        """
        response = self.tags_table.get_item(
            Key=dict(
                item_id=tag.item_id,
                group_name=tag.group_name,
            ),
            ConsistentRead=consistent_read,
        )

        if "Item" not in response:
            return None

        return Tag.from_dynamodb_item(response["Item"])

    def delete_tag(self, tag: Tag) -> Tag:
        """
        Idempotently remove a tag from an item
        """
        logger.info("Deleting %s", tag)
        self.tags_table.delete_item(
            Key=dict(
                item_id=tag.item_id,
                group_name=tag.group_name,
            )
        )
        return tag

    def get_tags_by_item(self, item: Item) -> List[Tag]:
        """
        Get all tags of a given item
        """
        # TODO: paginate and lazily yield from pages
        result = self.tags_table.query(
            KeyConditionExpression=Key("item_id").eq(item.item_id)
        )

        if "Items" not in result:
            return []

        return [Tag.from_dynamodb_item(result) for result in result["Items"]]

    def get_tags_by_group_name(self, tag_name: str) -> List[Tag]:
        """
        Get all tags with a given name
        """
        # TODO: paginate and yield from pages
        result = self.tags_table.query(
            IndexName=BANK_TAGS_INDEX_NAME,
            KeyConditionExpression=Key("group_name").eq(tag_name),
        )

        if "Items" not in result:
            return []

        return [Tag.from_dynamodb_item(result) for result in result["Items"]]

    def add_tag_group(self, tag_group: TagGroup) -> TagGroup:
        """
        Add a new tag group, overwriting any existing group info.
        """
        logger.info("Creating tag group %s", tag_group)
        self.tag_groups_table.put_item(Item=tag_group.dict())
        return tag_group

    def get_tag_group(
        self, group_name: str, consistent: bool = False
    ) -> Optional[TagGroup]:
        """
        Get a tag group if it exists
        """
        logger.info("Getting tag group %s", group_name)
        response = self.tag_groups_table.get_item(
            Key={"group_name": group_name},
            ConsistentRead=consistent,
        )
        return (
            TagGroup.from_dynamodb_item(response["Item"])
            if "Item" in response
            else None
        )

    def all_tag_groups(self) -> List[TagGroup]:
        """
        Get all tag groups
        """
        # TODO: paginate and lazily yield results
        result = self.tag_groups_table.scan()
        if "Items" not in result:
            return []

        return [TagGroup.from_dynamodb_item(result) for result in result["Items"]]

    def delete_tag_group(self, group: TagGroup, delete_tags = True) -> TagGroup:
        """
        Delete a tag group and optionally delete all tags with that group name
        """
        logger.info("Deleting %s", group)
        self.tag_groups_table.delete_item(
            Key=dict(
                group_name=group.group_name,
            )
        )

        if delete_tags:
            tags = self.get_tags_by_group_name(group.group_name)
            for tag in tags:
                self.delete_tag(tag)

        return group
