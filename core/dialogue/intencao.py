from dataclasses import dataclass
from enum import Enum


class Intencao(str, Enum):
    CUMPRIMENTAR = "CUMPRIMENTAR"
    ELOGIAR      = "ELOGIAR"
    AMEACAR      = "AMEACAR"
    DESPEDIR     = "DESPEDIR"
    NENHUMA      = "NENHUMA"


@dataclass
class DialogueResult:
    fala: str
    intencao: Intencao
    alvo_id: str | None = None
    intensidade: int = 5
