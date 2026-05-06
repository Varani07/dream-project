from dataclasses import dataclass, field
from core.entity.entity import Component

@dataclass
class LocalizacaoComponent(Component):
    regiao_nome: str = ""
    xy: tuple[int, int] = (0, 0)
    dentro_local: bool = True
    comodo:tuple[int,int]=(0,0)

@dataclass
class ConhecimentoMundoComponent(Component):
    locais_conhecidos:dict[str,dict[tuple[int,int],list[tuple[int,int]]]]=field(default_factory=dict)

    def add_local(self,nome_regiao:str,xy:tuple[int,int])->None:
        self.locais_conhecidos.setdefault(nome_regiao, {}).setdefault(xy, [])

    def add_comodo(self,nome_regiao:str,xy:tuple[int,int],c_xy:tuple[int,int])->None:
        self.locais_conhecidos.setdefault(nome_regiao, {}).setdefault(xy, []).append(c_xy)

    def local_conhecido(self,nome_regiao:str)->set[tuple[int,int]]:
        return set(local for local in self.locais_conhecidos.get(nome_regiao, {}).keys())
    
    def comodo_conhecido(self,nome_regiao:str,xy:tuple[int,int])->set[tuple[int,int]]:
        return set(
            local for local in self.locais_conhecidos
            .get(nome_regiao, {}).get(xy, [])
        )
