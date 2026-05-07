from dataclasses import dataclass, field
from typing import Self

from core.world.room import Room

LOCATION_TYPES: dict[str, dict] = {
    "residencia": {"glyph": "h", "color": "white", "description": "Uma casa simples."},
    "loja": {"glyph": "$", "color": "yellow", "description": "Uma loja com balcão."},
    "taverna": {"glyph": "T", "color": "red", "description": "Uma taverna abafada."},
    "praca": {"glyph": ".", "color": "green", "description": "Uma praça aberta."},
    "estrada": {"glyph": "-", "color": "white", "description": "Uma estrada de terra."}
}


@dataclass
class Location:
    region_name: str
    xy: tuple[int, int]
    location_type: str = "residencia"
    data_type: dict = field(default_factory=dict)
    rooms: list[Room] = field(default_factory=list)
    rooms_count:tuple[int,int]=(0,0)

    @property
    def description(self) -> str:
        return LOCATION_TYPES.get(self.location_type, {}).get("description", "Um lugar comum.")
    
    @property
    def glyph(self) -> str:
        return LOCATION_TYPES.get(self.location_type, {}).get("glyph", "?")
    
    @property
    def color(self)->str:
        return LOCATION_TYPES.get(self.location_type, {}).get("color", "white")

    def get_location(self, xy: tuple[int, int]) -> Room | None:
        return next(
            (room for room in self.rooms if room.xy == xy),
            None
        )
    
    @property
    def calculate_grid(self)->None:
        max_size_x = max(x.xy[0] for x in self.rooms)
        max_size_y = max(y.xy[1] for y in self.rooms)
        self.rooms_count=(max_size_x,max_size_y)

    def get_room(self, xy)->Room|None:
        return next(
            (room for room in self.rooms if room.xy == xy),
            None
        )
    
    @property
    def possible_rooms(self)->set[tuple[int,int]]:
        return set(room.xy for room in self.rooms)

    def to_dict(self) -> dict:
        return {
            "region_name": self.region_name,
            "xy": list(self.xy),
            "type": self.location_type,
            "data_type": self.data_type,
            "rooms": [comodo.to_dict() for comodo in self.rooms],
            "rooms_count": list(self.rooms_count)
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> Self:
        return cls(
            region_name=d["region_name"],
            xy=tuple(d['xy']),
            location_type=d.get("location_type", "residencia"),
            data_type=d.get("data_type", {}),
            rooms=[Room.from_dict(room) for room in d.get("rooms", [])],
            rooms_count=tuple(d['rooms_count'])
        )
    
    @classmethod
    def default_location(cls,region_name:str,xy:tuple[int,int],location_type:str) -> Self:
        inst=cls(
            region_name=region_name,
            xy=xy,
            location_type=location_type,
            rooms=[
                Room(
                    (0,0),
                    "comodo_generico"
                )
            ]
        )
        inst.calculate_grid
        return inst
    
    @classmethod
    def residence(cls,region_name:str,xy:tuple[int,int]) -> Self:
        inst=cls(
            region_name=region_name,
            xy=xy,
            location_type="residencia",
            rooms=[
                Room(
                    (0,0),
                    "sala",
                    locked=True
                ),
                Room(
                    (1,0),
                    "quarto"
                )
            ]
        )
        inst.calculate_grid
        return inst
