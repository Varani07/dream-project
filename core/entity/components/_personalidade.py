from dataclasses import dataclass, field
from core.entity.entity import Component


ARQUETIPOS_VALIDOS = ("amigavel", "rabugento", "devoto", "neutro")

@dataclass
class PersonalidadeComponent(Component):
    arquetipo: str = "neutro"
    humor: str = "neutro"            # neutro | sereno | feliz | triste | irritado


@dataclass
class AfinidadeComponent(Component):
    """Quanto outras Entities gostam desta. Visão DESTA Entity sobre os outros.

    `valor_por_id`: {entity_id_do_outro -> int}.

    Convenção de escala (0 = neutro):
    -100..-51 = ódio       -50..-21 = antipatia    -20..-1 = frio
    +1..+20 = simpático    +21..+50 = amigo        +51..+100 = leal
    """
    valor_por_id: dict[str, int] = field(default_factory=dict)

    def ajustar(self, outro_id: str, delta: int) -> int:
        atual = self.valor_por_id.get(outro_id, 0)
        novo = max(-100, min(100, atual + delta))
        self.valor_por_id[outro_id] = novo
        return novo
    