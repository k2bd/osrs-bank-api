from typing import Any, Dict, List

from humps import camelize

from osrs_items_api import items_service
from osrs_items_api.types import TagGroup


def assert_expected_item_json(item_json: Dict[str, Any], expected_item_id: int):
    """
    Assert that the json form of a retrieved item is correct,
    given the expected item ID
    """
    item = items_service.get_item(expected_item_id)
    assert item_json == camelize(item.dict())


def assert_expected_items_json(
    items_json: Dict[str, Any], expected_item_ids: List[int]
):
    """
    Assert that a list retrieved from the API is the JSON
    representation of the expected items
    """
    items = sorted(
        (items_service.get_item(item_id) for item_id in expected_item_ids),
        key=lambda i: i.item_id,
    )
    sorted_items_json = sorted(items_json["items"], key=lambda i: i["itemId"])

    assert sorted_items_json == [camelize(item.dict()) for item in items]


def assert_expected_tag_groups(
    groups_json: List[Dict[str, Any]], expected_groups: List[TagGroup]
):
    """
    Assert that a list retrieved from the API is the JSON
    representation of the expected tag goups
    """
    sorted_groups_json = sorted(groups_json, key=lambda g: g["groupName"])
    sorted_expected_groups = sorted(expected_groups, key=lambda g: g.group_name)

    assert sorted_groups_json == [
        camelize(group.dict()) for group in sorted_expected_groups
    ], (sorted_groups_json, sorted_expected_groups)
