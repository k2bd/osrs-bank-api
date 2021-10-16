from osrs_items_api import items_service
from osrs_items_api.tags_service import TagsService
from osrs_items_api.types import Tag


def test_add_and_get_tags(tags_service: TagsService):
    """
    Can add and retrieve tags
    """
    tag = Tag(item_id=1891, group_name="food")
    tags_service.add_tag(tag)
    assert tags_service.get_tag(tag) == tag


def test_add_tags_idempotent(tags_service: TagsService):
    """
    Can idempotently add tags
    """
    tag = Tag(item_id=1891, group_name="food")
    tags_service.add_tag(tag)
    tags_service.add_tag(tag)
    assert tags_service.get_tag(tag) == tag


def test_get_nonexistent_item(tags_service: TagsService):
    """
    Getting a nonexistent tag returns None
    """
    tag = Tag(item_id=1891, group_name="food")
    assert tags_service.get_tag(tag) is None


def test_delete_tag(tags_service: TagsService):
    """
    Can delete a tag
    """
    tag = Tag(item_id=1891, group_name="food")
    tags_service.add_tag(tag)
    tags_service.delete_tag(tag)
    assert tags_service.get_tag(tag) is None


def test_get_tags_by_item(tags_service: TagsService):
    """
    Can get all tags of a given item
    """
    bucket = items_service.get_item(1925)

    bucket_crafting_tag = Tag(item_id=1925, group_name="crafting")
    bucket_cooking_tag = Tag(item_id=1925, group_name="cooking")
    bucket_farming_tag = Tag(item_id=1925, group_name="farming")
    pie_dish_cooking_tag = Tag(item_id=2313, group_name="cooking")
    boots_lightness_travel_tag = Tag(item_id=88, group_name="travel")

    tags_service.add_tag(bucket_crafting_tag)
    tags_service.add_tag(bucket_cooking_tag)
    tags_service.add_tag(pie_dish_cooking_tag)
    tags_service.add_tag(bucket_farming_tag)
    tags_service.add_tag(boots_lightness_travel_tag)

    tags = tags_service.get_tags_by_item(bucket)

    assert len(tags) == 3
    assert set(tags) == {
        bucket_crafting_tag,
        bucket_cooking_tag,
        bucket_farming_tag,
    }


def test_get_tags_by_group_name(tags_service: TagsService):
    """
    Can get all tags of a given group name
    """
    copper_ore_ores_tag = Tag(item_id=436, group_name="ores")
    tin_ore_ores_tag = Tag(item_id=438, group_name="ores")
    iron_ore_ores_tag = Tag(item_id=440, group_name="ores")
    tags_service.add_tag(copper_ore_ores_tag)
    tags_service.add_tag(Tag(item_id=2349, group_name="bars"))  # Unrelated item + group
    tags_service.add_tag(tin_ore_ores_tag)
    tags_service.add_tag(
        Tag(item_id=436, group_name="favourite")
    )  # Wrong group, match item
    tags_service.add_tag(iron_ore_ores_tag)
    tags_service.add_tag(Tag(item_id=2351, group_name="bars"))  # Unrelated item + group

    tags = tags_service.get_tags_by_group_name("ores")

    assert len(tags) == 3
    assert set(tags) == {
        copper_ore_ores_tag,
        tin_ore_ores_tag,
        iron_ore_ores_tag,
    }
