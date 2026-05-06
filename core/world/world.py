from datetime import datetime
import uuid
from random import randint as ri
from typing import Self

from core.world.regiao import Regiao
from core.entity.entity import Entity
from core.entity.components import LocalizacaoComponent, ControlePlayerComponent


class World:
    def __init__(self, nome: str) -> None:
        self.id: str = str(uuid.uuid4())
        self.nome = nome
        self.regioes: list[Regiao] = []
        self.entities: list[Entity] = []
        self.tempo: datetime = datetime(1000, 1, 1, 7, 0)
        self.parent_save: str | None = None

    def add_regiao(self, regiao: Regiao) -> None:
        self.regioes.append(regiao)
    
    def get_regiao(self, nome: str) -> Regiao | None:
        return next(
            (regiao for regiao in self.regioes if regiao.nome == nome),
            None
        )
    
    def add_entity(self, entity: Entity) -> None:
        self.entities.append(entity)

    def get_entity(self, entity_id: str) -> Entity | None:
        return next(
            (e for e in self.entities if e.id == entity_id),
            None
        )

    def main_player(self) -> Entity | None:
        return next(
            (entity for entity in self.entities if entity.has(ControlePlayerComponent)),
            None
        )
    
    @classmethod
    def mundo_inicial(cls, player: Entity, nome_mundo: str = "Kazer") -> Self:
        inst = cls(nome_mundo)
        regiao = Regiao.cidade_inicial(nome_mundo=nome_mundo)
        residencias = [local for local in regiao.locais if local.tipo == "residencia"]
        local_inicial = residencias[0] if residencias else regiao.locais[ri(0, len(regiao.locais)-1)]
        loc = player.get(LocalizacaoComponent)
        if loc:
            loc.regiao_nome = regiao.nome
            loc.xy = local_inicial.xy
        inst.add_regiao(regiao)
        inst.add_entity(player)
        return inst
    