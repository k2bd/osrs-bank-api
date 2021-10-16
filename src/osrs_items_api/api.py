from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_camelcase import CamelModel
from mangum import Mangum
from starlette.responses import JSONResponse

from osrs_items_api import items_service
from osrs_items_api.logging import get_logger
from osrs_items_api.tags_service import TagsService
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


class ErrorMessage(CamelModel):
    """An error message with additional content"""

    message: str


# TODO: invert into app builder that accepts services that fill some interface
#       so e.g. we can unit test without needing docker


class ItemsSearchResult(CamelModel):
    #: Total number of items in the search result
    total_count: int

    #: The items returned on this page
    items: List[Item]


@app.get("/items", response_model=ItemsSearchResult)
def search_items(
    itemId: Optional[int] = None,
    nameLike: Optional[str] = "",
    includeMembers: bool = True,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    includeRelated: bool = False,
):
    """
    Search for items given some search criteria
    """
    logger.info("GET /items")

    items = sorted(items_service.main_items(), key=lambda i: i.item_id)

    if nameLike:
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

    # -- Pagination
    total_count = len(items)

    if offset is not None:
        logger.info("Adding offset of %s", offset)
        items = items[offset:]

    items = items[:limit] if limit is not None else items

    return ItemsSearchResult(
        total_count=total_count,
        last_result_id=items[-1].item_id,
        items=items,
    )

@app.get(
    "/item/{itemId}",
    response_model=Item,
    responses={404: {"model": ErrorMessage, "description": "The item does not exist"}},
)
def get_item(itemId: int):
    """
    Get an item by ID
    """
    logger.info("GET /item/%s", itemId)
    try:
        return items_service.get_item(itemId)
    except KeyError:
        return JSONResponse(
            status_code=404, content={"message": f"No item exists with ID {itemId}"}
        )


@app.get("item/{itemId}/related", response_model=List[Item])
def get_related_items(itemId: int):
    """
    Get all items related to the given main item
    """
    logger.info("GET /item/%s/related", itemId)
    item = items_service.get_item(itemId)
    return list(items_service.related_items(item))


@app.get("item/{itemId}/tags", response_model=List[Tag])
def get_item_tags(itemId: int):
    """
    Get the tags related to an item
    """
    logger.info("GET /item/%s/tags", itemId)
    tags_service = TagsService()
    item = items_service.get_item(item_id=itemId)
    return tags_service.get_tags_by_item(item)


@app.get("/tag/{groupName}/items", response_model=List[Item])
def get_items_by_tag(groupName: str):
    """
    Get items related to a given tag name
    """
    logger.info("GET /tag/%s/items", groupName)
    tags_service = TagsService()
    tags = tags_service.get_tags_by_group_name(groupName)
    return [items_service.get_item(tag.item_id) for tag in tags]


@app.post("/tag", response_model=Tag)
def post_tag(itemId: int, groupName: str):
    """
    Post a single tag
    """
    logger.info("POST /tag/ groupName=%s id=%s", groupName, itemId)
    tag = Tag(
        item_id=itemId,
        group_name=groupName,
    )
    tags_service = TagsService()
    return tags_service.add_tag(tag)


@app.delete("/tag")
def delete_tag(itemId: int, groupName: str):
    """
    Delete a single tag
    """
    logger.info("DELETE /tag/ groupName=%s id=%s", groupName, itemId)
    tag = Tag(
        item_id=itemId,
        group_name=groupName,
    )
    tags_service = TagsService()
    return tags_service.delete_tag(tag)


#: Handler for deploying to AWS Lambda
handler = Mangum(app)