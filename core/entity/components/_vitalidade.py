from dataclasses import dataclass
from core.entity.entity import Component

@dataclass
class VitalidadeComponent(Component):
    energia: int = 30
    energia_cap: int = 30
