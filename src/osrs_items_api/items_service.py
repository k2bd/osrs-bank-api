from typing import Generator, Iterable

from osrsbox import items_api

from osrs_items_api.types import Item

osrsbox_items = items_api.load()


def get_item(item_id: int) -> Item:
    """
    Get an item by ID
    """
    return Item.from_osrsbox(osrsbox_items.lookup_by_item_id(item_id))


def main_items() -> Generator[Item, None, None]:
    """
    Get main items, excluding things like stacked and noted forms
    """
    yield from filter_main_items(
        Item.from_osrsbox(osb_item) for osb_item in osrsbox_items
    )


def filter_main_items(items: Iterable[Item]) -> Generator[Item, None, None]:
    """
    Filter items for only main items
    """
    for item in items:
        osb_item = osrsbox_items.lookup_by_item_id(item.item_id)
        if not osb_item.linked_id_item:
            yield item


def search_items(keyword: str) -> Generator[Item, None, None]:
    """
    Search main items that match a keyword
    """
    yield from filter_main_items(
        Item.from_osrsbox(osb_item)
        for osb_item in osrsbox_items.search_item_names(keyword=keyword)
    )


def related_items(item: Item) -> Generator[Item, None, None]:
    """
    Get items related to a main item, such as stacked or noted forms
    """
    for related_item in osrsbox_items:
        if related_item.linked_id_item == item.item_id:
            yield Item.from_osrsbox(related_item)
