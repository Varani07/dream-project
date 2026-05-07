from core.events import (
    event_bus, SpeechEmitted, AffinityChanged, WorldLogMessage,
)
from core.entity.components import AffinityComponent
from core.dialogue.intention import Intention
from core.world.world import World


_AFFINITY_DELTA = {
    Intention.AMEACAR.value:      -1,
    Intention.ELOGIAR.value:      +1,
    Intention.CUMPRIMENTAR.value:  0,    # neutro
    Intention.DESPEDIR.value:      0,
    Intention.NENHUMA.value:       0,
}

_COLOR_BY_INTENTION = {
    Intention.AMEACAR.value:     "red",
    Intention.ELOGIAR.value:     "green",
    Intention.CUMPRIMENTAR.value:"cyan",
    Intention.DESPEDIR.value:    "dim",
    Intention.NENHUMA.value:     "white",
}


def register_dialogue_handlers(world: World) -> None:
    @event_bus.subscribe(SpeechEmitted)
    def _apply_affinity(ev: SpeechEmitted) -> None:
        if not ev.target_id:
            return
        target = world.get_entity(ev.target_id)
        sender = world.get_entity(ev.npc_id)
        if not (target and sender):
            return

        base = _AFFINITY_DELTA.get(ev.intention, 0)
        if base == 0:
            return
        delta = base * ev.intensity

        af = target.get(AffinityComponent)
        if af is None:
            af = AffinityComponent()
            target.add(af)
        new_af = af.adjust(sender.id, delta)

        event_bus.publish(AffinityChanged(
            from_id=target.id, to_id=sender.id,
            delta=delta, new_value=new_af,
        ))

    @event_bus.subscribe(SpeechEmitted)
    def _log_to_world(ev: SpeechEmitted) -> None:
        color = _COLOR_BY_INTENTION.get(ev.intention, "white")
        event_bus.publish(WorldLogMessage(
            text=f"[{color}][b]{ev.npc_name}:[/b] {ev.speech}[/]",
            color=color, channel="dialogo",
        ))
