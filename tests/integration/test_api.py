from fastapi.testclient import TestClient

from osrs_items_api.tags_service import TagsService
from osrs_items_api.types import Tag, TagGroup

from .helpers import (
    assert_expected_item_json,
    assert_expected_items_json,
    assert_expected_tag_groups,
)

DRAGON_LONGSWORD_SEARCH = "Dragon%20long"


def test_search_items_200_1(api_client: TestClient):
    """
    GET /items OK
    Searching for a single ID
    """
    result = api_client.get("/items?itemId=1891")
    assert result.status_code == 200
    assert_expected_items_json(result.json(), [1891])


def test_search_items_200_2(api_client: TestClient):
    """
    GET /items OK
    Searching for items related to a single ID
    (cake and its noted and placeholder forms)
    """
    result = api_client.get("/items?itemId=1891&includeRelated=1")
    assert result.status_code == 200
    assert_expected_items_json(result.json(), [1891, 1892, 19099])


def test_search_items_200_3(api_client: TestClient):
    """
    GET /items OK
    Name like
    """
    result = api_client.get(f"/items?nameLike={DRAGON_LONGSWORD_SEARCH}")
    assert result.status_code == 200
    assert_expected_items_json(result.json(), [1305])


def test_search_items_200_4(api_client: TestClient):
    """
    GET /items OK
    Exclude members
    """
    result = api_client.get(
        f"/items?nameLike={DRAGON_LONGSWORD_SEARCH}&includeMembers=0"
    )
    assert result.status_code == 200
    assert_expected_items_json(result.json(), [])


def test_search_items_200_5(tags_service: TagsService, api_client: TestClient):
    """
    GET /items OK
    By tags
    """
    tags_service.add_tag(Tag(item_id=123, group_name="A"))
    tags_service.add_tag(Tag(item_id=123, group_name="B"))
    tags_service.add_tag(Tag(item_id=456, group_name="A"))
    tags_service.add_tag(Tag(item_id=456, group_name="C"))
    tags_service.add_tag(Tag(item_id=789, group_name="A"))
    tags_service.add_tag(Tag(item_id=789, group_name="B"))

    result = api_client.get("/items?hasTags=A,C")
    assert result.status_code == 200
    assert_expected_items_json(result.json(), [456])


def get_item_200(api_client: TestClient):
    """
    GET /item/1891 OK
    """
    result = api_client.get("/item/1891")
    assert result.status_code == 200
    assert_expected_item_json(result.json(), 1891)


def get_item_404(api_client: TestClient):
    """
    GET /item/99999999999999 404
    Should be a valid test for a while...
    """
    result = api_client.get("/item/99999999999999")
    assert result.status_code == 404


def test_search_groups_200_1(tags_service: TagsService, api_client: TestClient):
    """
    Search by hasItems returns groups that have all the selected items
    """
    tags_service.add_tag(Tag(item_id=123, group_name="A"))
    tags_service.add_tag(Tag(item_id=123, group_name="B"))
    tags_service.add_tag(Tag(item_id=456, group_name="A"))
    tags_service.add_tag(Tag(item_id=456, group_name="C"))
    tags_service.add_tag(Tag(item_id=789, group_name="A"))
    tags_service.add_tag(Tag(item_id=789, group_name="B"))

    result = api_client.get("/groups?hasItems=123,456")

    assert result.status_code == 200
    assert_expected_tag_groups(
        result.json(),
        [
            TagGroup(group_name="A"),
        ],
    )
