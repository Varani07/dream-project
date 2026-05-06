from datetime import timedelta

from core.events import event_bus, TempoAvancou
from core.world.world import World


class TimeManager:
    def __init__(self, world: World, step_minutos: int = 5) -> None:
        self.world = world
        self.step_min = step_minutos

    def now(self) -> str:
        return self.world.tempo.strftime("%d/%m/%Y %H:%M")
    
    def _avancar(self, minutos: int, motivo: str) -> None:
        dia_antes = self.world.tempo.date()
        self.world.tempo += timedelta(minutes=minutos)
        event_bus.publish(TempoAvancou(
            minutos=minutos, novo_datetime=self.world.tempo, motivo=motivo,
            novo_dia=self.world.tempo.date() != dia_antes,
        ))

    def avancar_em_passos(self, minutos: int, motivo: str = "acao") -> None:
        if minutos <= 0:
            return
        for _ in range(minutos):
            self._avancar(1, motivo=motivo)
