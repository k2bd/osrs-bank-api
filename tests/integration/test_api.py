from fastapi.testclient import TestClient

from .helpers import assert_expected_item_json, assert_expected_items_json

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
    """
    result = api_client.get("/item/99999999999999")
    assert result.status_code == 404
