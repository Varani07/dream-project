from dataclasses import dataclass
from enum import Enum


class Intention(str, Enum):
    CUMPRIMENTAR = "CUMPRIMENTAR"
    ELOGIAR      = "ELOGIAR"
    AMEACAR      = "AMEACAR"
    DESPEDIR     = "DESPEDIR"
    NENHUMA      = "NENHUMA"


@dataclass
class DialogueResult:
    speech: str
    intention: Intention
    target_id: str | None = None
    intensity: int = 5
