from core.events import event_bus, TimeAdvanced
from core.entity.components import VitalityComponent
from core.world.world import World


def register(world: World) -> None:
    @event_bus.subscribe(TimeAdvanced)
    def _needs(ev: TimeAdvanced) -> None:
        for entity in world.entities:
            v = entity.get(VitalityComponent)
            if v is None:
                continue
            v.energy = max(0, v.energy - ev.minutes)