from core.events import (
    event_bus, FalaEmitida, AfinidadeMudou, LogMundoMensagem,
)
from core.entity.components import AfinidadeComponent
from core.dialogue.intencao import Intencao
from core.world.world import World


_DELTA_AFINIDADE = {
    Intencao.AMEACAR.value:      -1,
    Intencao.ELOGIAR.value:      +1,
    Intencao.CUMPRIMENTAR.value:  0,    # neutro
    Intencao.DESPEDIR.value:      0,
    Intencao.NENHUMA.value:       0,
}

_COR_POR_INTENCAO = {
    Intencao.AMEACAR.value:     "red",
    Intencao.ELOGIAR.value:     "green",
    Intencao.CUMPRIMENTAR.value:"cyan",
    Intencao.DESPEDIR.value:    "dim",
    Intencao.NENHUMA.value:     "white",
}


def registrar_handlers_dialogo(world: World) -> None:
    @event_bus.subscribe(FalaEmitida)
    def _aplicar_afinidade(ev: FalaEmitida) -> None:
        if not ev.alvo_id:
            return
        alvo = world.get_entity(ev.alvo_id)
        emissor = world.get_entity(ev.npc_id)
        if not (alvo and emissor):
            return

        base = _DELTA_AFINIDADE.get(ev.intencao, 0)
        if base == 0:
            return
        delta = base * ev.intensidade

        af = alvo.get(AfinidadeComponent)
        if af is None:
            af = AfinidadeComponent()
            alvo.add(af)
        novo = af.ajustar(emissor.id, delta)

        event_bus.publish(AfinidadeMudou(
            de_id=alvo.id, para_id=emissor.id,
            delta=delta, novo_valor=novo,
        ))

    @event_bus.subscribe(FalaEmitida)
    def _logar_no_mundo(ev: FalaEmitida) -> None:
        cor = _COR_POR_INTENCAO.get(ev.intencao, "white")
        event_bus.publish(LogMundoMensagem(
            texto=f"[{cor}][b]{ev.npc_nome}:[/b] {ev.fala}[/]",
            cor=cor, canal="dialogo",
        ))
