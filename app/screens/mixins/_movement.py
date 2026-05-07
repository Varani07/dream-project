from __future__ import annotations

from typing import Protocol, TYPE_CHECKING
if TYPE_CHECKING:
    from app.screens.game import GameRunning

from core.entity.entity import Entity
from core.entity.components import (
    LocationComponent, WorldKnowledgeComponent
)


class MovementProtocol(Protocol):
    loc:LocationComponent
    conhecimento_loc:WorldKnowledgeComponent

class MovementMixin:
    @staticmethod
    def _adjacent(a:tuple[int,int],b:tuple[int,int])->bool:
        return True
    
    def _click_cell(self:"MovementProtocol",xy:tuple[int,int])->None:
        pass