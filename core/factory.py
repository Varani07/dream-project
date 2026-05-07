from core.entity import create_player, create_npc
from core.world import World
from core.systems import register_systems
from core.entity.components import LocationComponent, WorldKnowledgeComponent


def new_world(player_name: str, world_name: str = "Kazer"):
    player = create_player(player_name)
    world = World.initial_world(player, world_name)
    player_loc = player.get(LocationComponent)
    assert player_loc is not None
    player.require(WorldKnowledgeComponent).add_room(
        player_loc.region_name,
        player_loc.xy,
        player_loc.room
    )

    bertrand = create_npc(
        "Bertrand", archetype="rabugento",
        region_name=world_name,
        xy=player_loc.xy, inside_location=True,
        room_xy=player_loc.room
    )
    world.add_entity(bertrand)

    return world