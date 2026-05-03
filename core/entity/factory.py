from core.entity.entity import Entity
from core.entity.components import (
    IdentidadeComponent, ControlePlayerComponent,
    VitalidadeComponent, LocalizacaoComponent
)


def criar_player(nome):
    e = Entity(nome)
    e.add(IdentidadeComponent(classe_social="comum", nome_publico=nome))
    e.add(VitalidadeComponent())
    e.add(LocalizacaoComponent())
    e.add(ControlePlayerComponent())
    return e

def criar_npc(nome):
    e = Entity(nome)
    e.add(IdentidadeComponent(classe_social="comum", nome_publico=nome))
    e.add(VitalidadeComponent())
    e.add(LocalizacaoComponent())
    return e

