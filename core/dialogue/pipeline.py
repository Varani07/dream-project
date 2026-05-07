from random import randint

from core.entity.entity import Entity
from core.entity.components import (
    PersonalityComponent, AffinityComponent, LocationComponent,
)
from core.events import event_bus, SpeechEmitted
from core.dialogue.intention import Intention, DialogueResult
from core.dialogue.templates import generate_speech


class DialoguePipeline:
    def decide_intention(self, npc: Entity, target: Entity) -> Intention:
        affinity = 0
        af = npc.get(AffinityComponent)
        if af:
            affinity = af.value_by_id.get(target.id, 0)

        if affinity <= -50:
            return Intention.AMEACAR
        if affinity >= 30:
            return Intention.ELOGIAR
        return Intention.CUMPRIMENTAR

    def generate_speech_from(self, npc: Entity, intention: Intention, target_name: str) -> str:
        pers = npc.get(PersonalityComponent)
        archetype = pers.archetype if pers else "neutro"
        return generate_speech(archetype, intention, target_name=target_name)

    def speak(self, npc: Entity, target: Entity, forced_intention: Intention | None = None) -> DialogueResult:
        intention = forced_intention or self.decide_intention(npc, target)
        speech = self.generate_speech_from(npc, intention, target_name=target.name)
        intensity = randint(3, 7)

        location_comp = npc.get(LocationComponent)
        location_xy = location_comp.xy if location_comp else None

        event_bus.publish(SpeechEmitted(
            npc_id=npc.id,
            npc_name=npc.name,
            speech=speech,
            intention=intention.value,    
            target_id=target.id,
            intensity=intensity,
            location_xy=location_xy,
        ))

        return DialogueResult(
            speech=speech, intention=intention,
            target_id=target.id, intensity=intensity,
        )
    