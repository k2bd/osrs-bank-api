from typing import Any, Dict, Optional, Type, TypeVar

from fastapi_camelcase import CamelModel
from osrsbox.items_api.item_properties import ItemProperties
from pydantic.main import BaseModel

from osrs_items_api.dynamodb import from_dynamodb

_T = TypeVar("_T")
_P = TypeVar("_P", bound=BaseModel)


class DynamoDBModel(CamelModel):
    @classmethod
    def from_dynamodb_item(cls: Type[_P], data: Dict[str, Any]) -> _P:
        return cls.parse_obj(from_dynamodb(data))


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


class Tag(DynamoDBModel):
    """
    An item tag
    """

    class Config:
        frozen = True

    #: Item ID the tag refers to
    item_id: int

    #: Name of the tag group
    group_name: str


class TagGroup(DynamoDBModel):
    """
    Info about a tag group
    """

    class Config:
        frozen = True

    #: Group name
    group_name: str

    #: Description
    description: Optional[str]

    #: ID of the icon item
    item_icon_id: Optional[int]
