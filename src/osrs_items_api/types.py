from typing import Type, TypeVar

from fastapi_camelcase import CamelModel
from osrsbox.items_api.item_properties import ItemProperties

_T = TypeVar("_T")


class Item(CamelModel):
    """
    An item in OSRS
    """

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

    #: Item ID the tag refers to
    item_id: int

    #: Name of the tag
    name: str
