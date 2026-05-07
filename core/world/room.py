from dataclasses import dataclass, field
from typing import Self

ROOM_TYPES: dict[str, dict] = {
    "sala": {"glyph": "*", "color": "white", "description": "Uma sala comum."},
    "quarto": {"glyph": "@", "color": "yellow", "description": "Um quarto comum."},
    "comodo_generico": {"glyph": "0", "color": "orange", "description": "Um lugar comum."}
}


@dataclass
class Room:
    xy: tuple[int, int]
    room_type: str = "quarto"
    data_type: dict = field(default_factory=dict)
    locked: bool = False

    @property
    def description(self) -> str:
        return ROOM_TYPES.get(self.room_type, {}).get("description", "Um lugar comum.")
    
    @property
    def glyph(self) -> str:
        return ROOM_TYPES.get(self.room_type, {}).get("glyph", "?")
    
    @property
    def color(self)->str:
        return ROOM_TYPES.get(self.room_type, {}).get("color", "white")
    
    def to_dict(self) -> dict:
        return {
            "xy": list(self.xy),
            "room_type": self.room_type,
            "data_type": self.data_type,
            "locked": self.locked
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> Self:
        return cls(
            xy=tuple(d['xy']),
            room_type=d.get("room_type", "residencia"),
            data_type=d.get("data_type", {}),
            locked=d.get("locked", False)
        )
