from dataclasses import dataclass
from core.entity.entity import Component

@dataclass
class IdentidadeComponent(Component):
    classe_social: str = "comum"
    nome_publico: str = ""

@dataclass
class ControlePlayerComponent(Component):
    """Marker — sem campos. Diferencia player de NPC."""
    pass
