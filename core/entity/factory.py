from random import choice

from core.entity.entity import Entity
from core.entity.components import (
    IdentidadeComponent, ControlePlayerComponent,
    VitalidadeComponent, LocalizacaoComponent,
    PersonalidadeComponent, AfinidadeComponent,
    ConhecimentoMundoComponent,
    ARQUETIPOS_VALIDOS
)


def criar_player(nome:str):
    e = Entity(nome)
    e.add(IdentidadeComponent(classe_social="comum", nome_publico=nome))
    e.add(VitalidadeComponent())
    e.add(PersonalidadeComponent())
    e.add(AfinidadeComponent())

    e.add(LocalizacaoComponent())
    e.add(ConhecimentoMundoComponent())

    e.add(ControlePlayerComponent())
    return e


def criar_npc(
        nome:str,arquetipo:str="neutro",regiao_nome:str="Kazer",
        xy:tuple[int, int]=(0, 0),dentro_local:bool=False,
        c_xy:tuple[int,int]=(0,0)) -> Entity:
    
    n = Entity(nome)
    n.add(IdentidadeComponent(classe_social="comum", nome_publico=nome))
    n.add(VitalidadeComponent())
    n.add(PersonalidadeComponent(arquetipo=arquetipo))
    n.add(AfinidadeComponent())

    n.add(LocalizacaoComponent(
        regiao_nome=regiao_nome, xy=xy, 
        dentro_local=dentro_local, comodo=c_xy,
    ))
    conhecimento_mundo = ConhecimentoMundoComponent()
    conhecimento_mundo.add_comodo(regiao_nome,xy,c_xy)
    n.add(conhecimento_mundo)
    return n
