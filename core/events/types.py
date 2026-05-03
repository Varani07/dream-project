from dataclasses import dataclass
from datetime import datetime
from core.events.bus import Event

@dataclass
class TempoAvancou(Event):
    minutos: int
    novo_datetime: datetime
    motivo: str
    novo_dia: bool = False

@dataclass
class LogMundoMensagem(Event):
    texto: str
    cor: str = "white"
    canal: str = "geral"

@dataclass
class FalaEmitida(Event):
    npc_id: str
    npc_nome: str
    fala: str
    intencao: str
    alvo_id: str | None = None
