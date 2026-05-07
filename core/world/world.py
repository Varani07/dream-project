from datetime import datetime
import uuid
from random import randint as ri
from typing import Self

from core.world.region import Region
from core.entity.entity import Entity
from core.entity.components import LocationComponent, PlayerControlComponent


class World:
    def __init__(self, name: str) -> None:
        self.id: str = str(uuid.uuid4())
        self.name = name
        self.regions: list[Region] = []
        self.entities: list[Entity] = []
        self.time: datetime = datetime(1000, 1, 1, 7, 0)
        self.parent_save: str | None = None

    def add_region(self, region: Region) -> None:
        self.regions.append(region)
    
    def get_region(self, name: str) -> Region | None:
        return next(
            (region for region in self.regions if region.name == name),
            None
        )
    
    def add_entity(self, entity: Entity) -> None:
        self.entities.append(entity)

    def get_entity(self, entity_id: str) -> Entity | None:
        return next(
            (e for e in self.entities if e.id == entity_id),
            None
        )

    def main_player(self) -> Entity | None:
        return next(
            (entity for entity in self.entities if entity.has(PlayerControlComponent)),
            None
        )
    
    @classmethod
    def initial_world(cls, player: Entity, world_name: str = "Kazer") -> Self:
        inst = cls(world_name)
        region = Region.initial_city(world_name=world_name)
        residences = [locations for locations in region.locations if locations.location_type == "residencia"]
        initial_location = residences[0] if residences else region.locations[ri(0, len(region.locations)-1)]
        loc = player.get(LocationComponent)
        if loc:
            loc.region_name = region.name
            loc.xy = initial_location.xy
        inst.add_region(region)
        inst.add_entity(player)
        return inst
    