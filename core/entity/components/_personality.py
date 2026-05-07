from dataclasses import dataclass, field
from core.entity.entity import Component


VALID_ARCHETYPES = ("amigavel", "rabugento", "devoto", "neutro")

@dataclass
class PersonalityComponent(Component):
    archetype: str = "neutro"
    mood: str = "neutro"            # neutro | sereno | feliz | triste | irritado


@dataclass
class AffinityComponent(Component):
    """Quanto outras Entities gostam desta. Visão DESTA Entity sobre os outros.

    `valor_por_id`: {entity_id_do_outro -> int}.

    Convenção de escala (0 = neutro):
    -100..-51 = ódio       -50..-21 = antipatia    -20..-1 = frio
    +1..+20 = simpático    +21..+50 = amigo        +51..+100 = leal
    """
    value_by_id: dict[str, int] = field(default_factory=dict)

    def adjust(self, other_id: str, delta: int) -> int:
        current = self.value_by_id.get(other_id, 0)
        new_value = max(-100, min(100, current + delta))
        self.value_by_id[other_id] = new_value
        return new_value
    