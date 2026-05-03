from core.events import event_bus, TempoAvancou
from core.entity.components import VitalidadeComponent
from core.world.world import World


def registrar(world: World) -> None:
    @event_bus.subscribe(TempoAvancou)
    def _necessidades(ev: TempoAvancou) -> None:
        for entity in world.entities:
            v = entity.get(VitalidadeComponent)
            if v is None:
                continue
            v.energia = max(0, v.energia - ev.minutos)