from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_camelcase import CamelModel
from mangum import Mangum
from starlette.responses import JSONResponse

from osrs_items_api import items_service
from osrs_items_api import tags_service
from osrs_items_api.logging import get_logger
from osrs_items_api.tags_service import TagsService
from osrs_items_api.types import Item, Tag, TagGroup

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

# TODO: Async API


class ItemsSearchResult(CamelModel):
    #: Total number of items in the search result
    total_count: int

    #: The items returned on this page
    items: List[Item]


@app.get("/items", response_model=ItemsSearchResult)
def search_items(
    itemId: Optional[int] = None,
    nameLike: Optional[str] = None,
    includeMembers: bool = True,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    includeRelated: bool = False,
    hasTags: Optional[str] = None,
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

    if hasTags:
        tags_set = set(hasTags.split(","))
        logger.info("Filtering by tags")
        tags_service = TagsService()
        item_tags = {
            item.item_id: {
                tag.group_name for tag in tags_service.get_tags_by_item(item)
            }
            for item in items
        }
        items = [item for item in items if tags_set <= item_tags[item.item_id]]

    # -- Add related

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


@app.get("/items/related/{itemId}", response_model=List[Item])
def get_related_items(itemId: int):
    """
    Get all items related to the given main item
    """
    logger.info("GET /items/related/%s", itemId)
    item = items_service.get_item(itemId)
    return list(items_service.related_items(item))


@app.get("/tags/item/{itemId}", response_model=List[Tag])
def get_item_tags(itemId: int):
    """
    Get the tags related to an item
    """
    logger.info("GET /tags/item/%s", itemId)
    tags_service = TagsService()
    item = items_service.get_item(item_id=itemId)
    return tags_service.get_tags_by_item(item)


@app.get("/items/tag/{groupName}", response_model=List[Item])
def get_items_by_tag(groupName: str, includeRelated: Optional[bool] = False):
    """
    Get items that belong to a tag group
    """
    logger.info("GET /items/tag/%s", groupName)
    tags_service = TagsService()
    tags = tags_service.get_tags_by_group_name(groupName)
    items = list(
        items_service.filter_main_items(
            (items_service.get_item(tag.item_id) for tag in tags)
        )
    )

    if includeRelated:
        new_items: List[Item] = []
        for item in items:
            new_items.extend(items_service.related_items(item))
        items += new_items

    return items


def _add_tag(
    tags_service: TagsService, tag: Tag, include_related: Optional[bool] = False
):
    tags = [tag]
    if include_related:
        item = items_service.get_item(tag.item_id)
        tags.extend(
            Tag(item_id=item.item_id, group_name=tag.group_name)
            for item in items_service.related_items(item)
        )
        logger.info("Including %s", tags)

    return [tags_service.add_tag(t) for t in tags]


@app.post("/tag", response_model=List[Tag])
def post_tag(tag: Tag, includeRelated: Optional[bool] = False):
    """
    Post a single tag
    """
    logger.info("POST /tag/ tag=%s", tag)
    return _add_tag(tags_service=TagsService(), tag=tag, include_related=includeRelated)


@app.post("/tags", response_model=List[Tag])
def post_tags(tags: List[Tag], includeRelated: Optional[bool] = False):
    """
    Post several tags
    """
    logger.info("POST /tags/ tags=%s", tags)
    tags_service = TagsService()

    result = []
    for tag in tags:
        result.extend(
            _add_tag(tags_service=tags_service, tag=tag, include_related=includeRelated)
        )


def _delete_tag(
    tags_service: TagsService, tag: Tag, include_related: Optional[bool] = False
):
    tags = [tag]
    if include_related:
        item = items_service.get_item(tag.item_id)
        tags.extend(
            Tag(item_id=item.item_id, group_name=tag.group_name)
            for item in items_service.related_items(item)
        )
        logger.info("Including %s", tags)

    return [tags_service.delete_tag(t) for t in tags]


@app.delete("/tag", response_model=List[Tag])
def delete_tag(tag: Tag, includeRelated: Optional[bool] = False):
    """
    Delete a single tag
    """
    logger.info("DELETE /tag/ tag=%s", tag)
    return _delete_tag(
        tags_service=TagsService(), tag=tag, include_related=includeRelated
    )


@app.delete("/tags", response_model=List[Tag])
def delete_tags(tags: List[Tag], includeRelated: Optional[bool] = False):
    """
    Delete several tags
    """
    logger.info("DELETE /tags/ tags=%s", tags)
    tags_service = TagsService()

    result = []
    for tag in tags:
        result.extend(
            _delete_tag(
                tags_service=tags_service, tag=tag, include_related=includeRelated
            )
        )


@app.get("/tagGroups", response_model=List[str], deprecated=True)
def search_tag_groups(nameLike: Optional[str] = None):
    """
    Get tag group names
    """
    tags_service = TagsService()
    groups = [tag_group.group_name for tag_group in tags_service.all_tag_groups()]
    if nameLike:
        groups = [group for group in groups if nameLike.lower() in group.lower()]
    return groups


@app.get("/group/{groupName}", response_model=TagGroup)
def delete_group(groupName: str):
    """
    Get a tag group
    """
    tags_service = TagsService()
    return tags_service.get_tag_group(groupName)


@app.delete("/group", response_model=TagGroup)
def delete_group(group: TagGroup):
    """
    Delete a tag group and all connected tags
    """
    tags_service = TagsService()
    tags_service.delete_tag_group(group, delete_tags=True)
    return group


@app.put("/group", response_model=TagGroup)
def put_group(group: TagGroup):
    """
    Create/update a group
    """
    logger.info("Putting tag group: %s", group)
    tags_service = TagsService()
    tags_service.add_tag_group(group)
    return group


@app.get("/groups", response_model=List[TagGroup])
def search_groups(nameLike: Optional[str] = None, hasItems: Optional[str] = None):
    """
    Get tag groups
    """
    tags_service = TagsService()
    groups = tags_service.all_tag_groups()

    if nameLike:
        groups = [
            group for group in groups if nameLike.lower() in group.group_name.lower()
        ]

    if hasItems is not None:
        items_set = {int(item_id) for item_id in hasItems.split(",")}
        group_tags = {
            group.group_name: {
                tag.item_id
                for tag in tags_service.get_tags_by_group_name(group.group_name)
            }
            for group in groups
        }
        groups = [
            group for group in groups if items_set <= group_tags[group.group_name]
        ]

    return groups


#: Handler for deploying to AWS Lambda
handler = Mangum(app)
