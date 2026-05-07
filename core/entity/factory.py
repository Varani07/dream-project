from random import choice

from core.entity.entity import Entity
from core.entity.components import (
    IdentityComponent, PlayerControlComponent,
    VitalityComponent, LocationComponent,
    PersonalityComponent, AffinityComponent,
    WorldKnowledgeComponent,
    VALID_ARCHETYPES
)


def create_player(name:str):
    e = Entity(name)
    e.add(IdentityComponent(social_class="comum", public_name=name))
    e.add(VitalityComponent())
    e.add(PersonalityComponent())
    e.add(AffinityComponent())

    e.add(LocationComponent())
    e.add(WorldKnowledgeComponent())

    e.add(PlayerControlComponent())
    return e


def create_npc(
        name:str,archetype:str="neutro",region_name:str="Kazer",
        xy:tuple[int, int]=(0, 0),inside_location:bool=False,
        room_xy:tuple[int,int]=(0,0)) -> Entity:
    
    n = Entity(name)
    n.add(IdentityComponent(social_class="comum", public_name=name))
    n.add(VitalityComponent())
    n.add(PersonalityComponent(archetype=archetype))
    n.add(AffinityComponent())

    n.add(LocationComponent(
        region_name=region_name, xy=xy, 
        inside_location=inside_location, room=room_xy,
    ))
    n.add(WorldKnowledgeComponent().add_room(region_name,xy,room_xy))
    return n
