from typing import Any, Dict, Type, TypeVar

from fastapi_camelcase import CamelModel
from osrsbox.items_api.item_properties import ItemProperties

from osrs_items_api.dynamodb import from_dynamodb

_T = TypeVar("_T")


class Item(CamelModel):
    """
    An item in OSRS
    """

    class Config:
        frozen = True

    #: Ingame ID of the item
    item_id: int

    #: Name of the item
    name: str

    #: If the item is members-only
    members: bool

    #: Base-64 encoded icon
    icon_base64: str

    @classmethod
    def from_osrsbox(cls: Type[_T], item: ItemProperties) -> _T:
        return Item(
            item_id=item.id,
            name=item.name,
            members=item.members,
            icon_base64=item.icon,
        )


class Tag(CamelModel):
    """
    An item tag
    """

    class Config:
        frozen = True

    #: Item ID the tag refers to
    item_id: int

    #: Name of the tag group
    group_name: str

    @classmethod
    def from_dynamodb_item(cls: Type[_T], data: Dict[str, Any]) -> _T:
        return Tag.parse_obj(from_dynamodb(data))
