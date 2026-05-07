from typing import Self

from dataclasses import dataclass, field
from core.entity.entity import Component

@dataclass
class LocationComponent(Component):
    region_name:str=""
    xy: tuple[int,int]=(0,0)
    inside_location:bool=True
    room:tuple[int,int]=(0,0)

@dataclass
class WorldKnowledgeComponent(Component):
    known_locations:dict[str,dict[tuple[int,int],list[tuple[int,int]]]]=field(default_factory=dict)

    def add_location(self,region_name:str,xy:tuple[int,int])->None:
        self.known_locations.setdefault(region_name, {}).setdefault(xy, [])

    def add_room(self,region_name:str,xy:tuple[int,int],room_xy:tuple[int,int])->Self:
        self.known_locations.setdefault(region_name, {}).setdefault(xy, []).append(room_xy)
        return self

    def get_known_places(self,region_name:str)->set[tuple[int,int]]:
        return set(place for place in self.known_locations.get(region_name, {}).keys())
    
    def get_known_rooms(self,region_name:str,xy:tuple[int,int])->set[tuple[int,int]]:
        return set(
            room for room in self.known_locations
            .get(region_name, {}).get(xy, [])
        )
