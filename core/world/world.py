from datetime import datetime
from random import choice
import uuid

from core.world.regiao import Regiao
from core.npc.npc import Npc
import core.world.local as l


class World():
    def __init__(self, nome:str) -> None:
        self.id = str(uuid.uuid4())
        self.nome = nome
        self.regioes = []
        self.npcs = []
        self.tempo = datetime(1000, 1, 1, 7, 0)
        self.parent = None

    def add_regiao(self, regiao:Regiao) -> None:
        self.regioes.append(regiao)

    def add_npc(self, npc:Npc, nome_regiao:str) -> None:
        for regiao in self.regioes:
            if regiao.nome == nome_regiao:
                pass
        self.npcs.append(npc)

    @classmethod
    def mundo_inicial(cls, npc:Npc):
        inst = cls("Mundo Inicial")
        
        regiao = Regiao.cidade_inicial(inst.nome)
        local = choice([locais for locais in regiao.locais if isinstance(locais, l.Residencia)])

        npc.locais_conhecidos[local.nome_regiao] = {local.xy: local}
        npc.info_local_atual = local # type: ignore
        npc.local_atual = local.xy
        npc.dentro_local = True
        npc.npc = False
        
        inst.add_regiao(regiao)
        inst.npcs.append(npc)
        return inst
    
    def main_player(self) -> Npc:
        for npc in self.npcs:
            if not npc.npc:
                return npc
        return npc # type: ignore

    def get_regiao(self, nome_regiao:str) -> Regiao:
        regiao = next(
            (r for r in self.regioes if r.nome == nome_regiao),
            None
        )
        return regiao # type: ignore
