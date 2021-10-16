from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from osrs_items_api import items_service
from osrs_items_api.logging import get_logger
from osrs_items_api.types import Item, Tag

logger = get_logger()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/items", response_model=List[Item])
def search_items(
    itemId: Optional[int] = None,
    nameLike: str = "",
    includeMembers: bool = True,
    limit: Optional[int] = None,
    exclusiveStartId: Optional[int] = None,
    includeRelated: bool = False,
):
    """
    Search for items given some search criteria
    """
    logger.info("GET /items")

    logger.info("Filtering by name %s", nameLike)
    items = sorted(items_service.search_items(nameLike), key=lambda i: i.item_id)

    if itemId:
        logger.info("Filtering by ID %s", itemId)
        items = [item for item in items if item.item_id == itemId]

    if not includeMembers:
        logger.info("Filtering by non-members items")
        items = [item for item in items if not item.members]

    if includeRelated:
        logger.info("Adding related items")
        extra_items = []
        for item in items:
            extra_items.extend(list(items_service.related_items(item)))

        items = sorted(items + extra_items, key=lambda i: i.item_id)

    if exclusiveStartId is not None:
        logger.info("Filtering by items with ID > %s", exclusiveStartId)
        items = [item for item in items if item.item_id > exclusiveStartId]

    return items[:limit] if limit is not None else items


@app.get("/item/{id}", response_model=Item)
def get_item(id: int):
    """
    Get an item by ID
    """
    logger.info("GET /item/%s", id)
    return items_service.get_item(id)


@app.get("item/{id}/related", response_model=List[Item])
def get_related_items(id: int):
    """
    Get all items related to the given main item (including itself)
    """
    logger.info("GET /item/%s/related", id)
    item = items_service.get_item(id)
    return [item] + list(items_service.related_items(item))


@app.get("item/{id}/tags", response_model=List[Tag])
def get_item_tags(id: int):
    """
    Get the tags related to an item
    """
    logger.info("GET /item/%s/tags", id)


@app.get("/tag/{name}", response_model=Tag)
def get_tag(name: str):
    """
    Get a single tag by name
    """
    logger.info("GET /tag/%s", name)


@app.get("/tag/{name}/items", response_model=List[Item])
def get_items_by_tag(name: str):
    """
    Get items related to a given tag name
    """
    logger.info("GET /tag/%s/items", name)


@app.post("/tag/", response_model=Tag)
def post_tag(itemId: int, groupName: str):
    """
    Post a single tag
    """
    logger.info("POST /tag/ groupName=%s id=%s", groupName, itemId)


@app.delete("/tag")
def delete_tag(itemId: int, groupName: str):
    """
    Delete a single tag
    """
    logger.info("DELETE /tag/ groupName=%s id=%s", groupName, itemId)


#: Handler for deploying to AWS Lambda
handler = Mangum(app)
