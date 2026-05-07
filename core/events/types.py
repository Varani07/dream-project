from dataclasses import dataclass
from datetime import datetime
from core.events.bus import Event

@dataclass
class TimeAdvanced(Event):
    minutes: int
    new_datetime: datetime
    reason: str
    new_day: bool = False

@dataclass
class WorldLogMessage(Event):
    text: str
    color: str = "white"
    channel: str = "geral"

@dataclass
class SpeechEmitted(Event):
    npc_id: str
    npc_name: str
    speech: str
    intention: str
    target_id: str | None = None
    intensity: int = 5
    location_xy: tuple[int, int] | None = None

@dataclass
class AffinityChanged(Event):
    from_id: str
    to_id: str
    delta: int
    new_value: int
