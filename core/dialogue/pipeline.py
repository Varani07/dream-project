from random import randint

from core.entity.entity import Entity
from core.entity.components import (
    PersonalidadeComponent, AfinidadeComponent, LocalizacaoComponent,
)
from core.events import event_bus, FalaEmitida
from core.dialogue.intencao import Intencao, DialogueResult
from core.dialogue.templates import gerar_fala


class DialoguePipeline:
    def decidir_intencao(self, npc: Entity, alvo: Entity) -> Intencao:
        afinidade = 0
        af = npc.get(AfinidadeComponent)
        if af:
            afinidade = af.valor_por_id.get(alvo.id, 0)

        if afinidade <= -50:
            return Intencao.AMEACAR
        if afinidade >= 30:
            return Intencao.ELOGIAR
        return Intencao.CUMPRIMENTAR

    def gerar_fala_de(self, npc: Entity, intencao: Intencao, alvo_nome: str) -> str:
        pers = npc.get(PersonalidadeComponent)
        arquetipo = pers.arquetipo if pers else "neutro"
        return gerar_fala(arquetipo, intencao, alvo_nome=alvo_nome)

    def falar(self, npc: Entity, alvo: Entity, intencao_forcada: Intencao | None = None) -> DialogueResult:
        intencao = intencao_forcada or self.decidir_intencao(npc, alvo)
        fala = self.gerar_fala_de(npc, intencao, alvo_nome=alvo.nome)
        intensidade = randint(3, 7)

        loc = npc.get(LocalizacaoComponent)
        local_xy = loc.xy if loc else None

        event_bus.publish(FalaEmitida(
            npc_id=npc.id,
            npc_nome=npc.nome,
            fala=fala,
            intencao=intencao.value,    
            alvo_id=alvo.id,
            intensidade=intensidade,
            local_xy=local_xy,
        ))

        return DialogueResult(
            fala=fala, intencao=intencao,
            alvo_id=alvo.id, intensidade=intensidade,
        )
    