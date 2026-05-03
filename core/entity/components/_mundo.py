from dataclasses import dataclass
from core.entity.entity import Component

@dataclass
class LocalizacaoComponent(Component):
    regiao_nome: str = ""
    xy: tuple[int, int] = (0, 0)
    dentro_local: bool = True
