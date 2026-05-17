from __future__ import annotations

from typing import Protocol, TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from app.screens.game import GameRunning

from app.widgets.map import MiniMap

from core.entity import Entity
from core.world import Region
from core.entity.components import (
    LocationComponent, WorldKnowledgeComponent
)


class MovementProtocol(Protocol):
    loc:LocationComponent
    world_knowledge:WorldKnowledgeComponent

    player:Entity
    world_region:Region

    _map:MiniMap

    direction:str

    def _next_location(self,direction:str)->tuple[int,int]:...
    def notify(self,message:str,timeout:float|None=None)->None:...


class MovementMixin:
    # refazer
    def _move(self:"MovementProtocol",direction:str)->None:
        next_location=self._next_location(direction)
        possible_locations=self.world_region.get_possible_locations(self.loc.inside_location,self.loc.xy)
        loc = next((location for location in possible_locations if location[0]==next_location),None)
        if loc is not None:
            if loc[1]:
                self.notify("Local trancado.",timeout=1)
            else:
                if len(self.direction)==0 or self.direction != direction:
                    self.notify("Gasto por volta de 5 de energia.",timeout=1)
                    self.direction = direction      
                else:
                    if self.loc.inside_location:
                        self.loc.room=next_location
                        self._map.update(
                            self.world_knowledge.get_known_rooms(
                                self.world_region.name,
                                self.player.get_location_xy
                            ),
                            next_location
                        )
                    else:
                        self.loc.xy=next_location
                        self._map.update(
                            self.world_knowledge.get_known_places(
                                self.world_region.name
                            ),
                            next_location
                        )
                    self.direction=""
        else:
            self.direction=""

    def _next_location(self:"MovementProtocol",direction:str)->tuple[int,int]:
        x,y=self.player.get_location_xy
        match direction:
            case "left": return (x-1,y)
            case "right": return (x+1,y)
            case "up": return (x,y-1)
            case _: return (x,y+1)
