from random import choices
from core.world.location import Location
from typing import Self


INITIAL_CITY_COMPOSITION: list[tuple[str, int]] = [
    ("residencia", 4),
    ("loja", 2),
    ("taverna", 1),
    ("praca", 1)
]


class Region:
    def __init__(self, world_name: str, name: str = "") -> None:
        self.world_name = world_name
        self.name = name
        self.composition: list[tuple[str, int]] = []
        self.locations: list[Location] = []
        self.locations_count: tuple[int, int] = (0, 0)

    def generate_locations(self, size: tuple[int, int] = (6, 5)) -> None:
        self.locations_count = size
        types = [t[0] for t in self.composition]
        weights = [t[1] for t in self.composition]
        for x in range(size[0]):
            for y in range(size[1]):
                location_type = choices(types, weights=weights, k=1)[0]
                match location_type:
                    case 'residencia':
                        location = Location.residence(self.name,(x,y))
                    case _:
                        location = Location.default_location(self.name,(x,y),location_type)
                self.locations.append(location)

    def get_location(self, xy: tuple[int, int]) -> Location | None:
        return next(
            (location for location in self.locations if location.xy == xy),
            None
        )
    
    def get_possible_locations(self,inside:bool=False,current_location:tuple[int,int]|None=None)->set[tuple[int,int]]:
        if inside and current_location is not None:
            location = self.get_location(current_location)
            assert location is not None
            return set(room.xy for room in location.rooms)
        else:
            return set(location.xy for location in self.locations)
    
    @classmethod
    def initial_city(cls, world_name: str) -> Self:
        inst = cls(world_name, name="Cidade Inicial")
        inst.composition = INITIAL_CITY_COMPOSITION
        inst.generate_locations()
        return inst
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "world_name": self.world_name,
            "composition": [list(t) for t in self.composition],
            "locations_count": list(self.locations_count),
            "locations": [location.to_dict() for location in self.locations],
        }

    @classmethod
    def from_dict(cls, d: dict) -> Self:
        inst = cls(d["world_name"], name=d["name"])
        inst.composition = [tuple(t) for t in d.get("composition", [])]
        inst.locations_count = tuple(d["locations_count"])
        inst.locations = [Location.from_dict(location) for location in d.get("locations", [])]
        return inst
    