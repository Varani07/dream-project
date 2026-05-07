from textual.widgets import Static

from core.entity.entity import Entity
from core.entity.components import VitalityComponent, LocationComponent


def _bar(value: int, cap: int, width: int = 10, color: str = "green") -> str:
    if cap <= 0:
        return f"[{color}]{'░' * width}[/]"
    fill = max(0, min(width, value * width // cap))
    return f"[{color}]{'█' * fill}{'░' * (width - fill)}[/] {value}/{cap}"


class PainelStatus(Static):
    def __init__(self, player: Entity, **kw):
        super().__init__("", **kw)
        self.player = player

    def update_status(self, player: Entity, time_str: str = "", location_name: str = "") -> None:
        self.player = player
        self.lines = [f"[b cyan]{player.name}[/]"]

        self._vitality

        loc = player.get(LocationComponent)
        if loc:
            inout = "dentro" if loc.inside_location else "fora"
            name = location_name or loc.region_name
            self.lines.append(f"[dim]📍 {name} ({inout})[/]")

        if time_str:
            self.lines.append(f"[dim]🕘 {time_str}[/]")

        self.update("\n".join(self.lines))

    @property
    def _vitality(self) -> None:
        v = self.player.get(VitalityComponent)
        if v:
            color = (
                "red" if v.energy <= v.cap // 4
                else "yellow" if v.energy <= v.cap // 2
                else "green"
            )
            self.lines.append(f"[{color}]❤ Energia[/] {_bar(v.energy, v.cap, color=color)}")
