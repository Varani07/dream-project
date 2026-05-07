from dataclasses import dataclass
from core.entity.entity import Component

@dataclass
class VitalityComponent(Component):
    energy: int = 30
    cap: int = 30
