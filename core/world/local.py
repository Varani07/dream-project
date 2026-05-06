from dataclasses import dataclass, field
from typing import Self

from core.world.comodo import Comodo

TIPOS_LOCAL: dict[str, dict] = {
    "residencia": {"glyph": "h", "cor": "white", "descricao": "Uma casa simples."},
    "loja": {"glyph": "$", "cor": "yellow", "descricao": "Uma loja com balcão."},
    "taverna": {"glyph": "T", "cor": "red", "descricao": "Uma taverna abafada."},
    "praca": {"glyph": ".", "cor": "green", "descricao": "Uma praça aberta."},
    "estrada": {"glyph": "-", "cor": "white", "descricao": "Uma estrada de terra."}
}


@dataclass
class Local:
    nome_regiao: str
    xy: tuple[int, int]
    tipo: str = "residencia"
    tipo_data: dict = field(default_factory=dict)
    comodos: list[Comodo] = field(default_factory=list)
    num_comodos:tuple[int,int]=(0,0)

    @property
    def descricao(self) -> str:
        return TIPOS_LOCAL.get(self.tipo, {}).get("descricao", "Um lugar comum.")
    
    @property
    def glyph(self) -> str:
        return TIPOS_LOCAL.get(self.tipo, {}).get("glyph", "?")
    
    @property
    def cor(self)->str:
        return TIPOS_LOCAL.get(self.tipo, {}).get("cor", "white")

    def get_local(self, xy: tuple[int, int]) -> Comodo | None:
        return next(
            (local for local in self.comodos if local.xy == xy),
            None
        )
    
    @property
    def calcular_grid(self)->None:
        tamanho_max_x = max(x.xy[0] for x in self.comodos)
        tamanho_max_y = max(y.xy[1] for y in self.comodos)
        self.num_comodos=(tamanho_max_x,tamanho_max_y)

    def get_comodo(self, xy)->Comodo|None:
        return next(
            (comodo for comodo in self.comodos if comodo.xy == xy),
            None
        )
    
    @property
    def possiveis_comodos(self)->set[tuple[int,int]]:
        return set(comodo.xy for comodo in self.comodos)

    def to_dict(self) -> dict:
        return {
            "nome_regiao": self.nome_regiao,
            "xy": list(self.xy),
            "tipo": self.tipo,
            "tipo_data": self.tipo_data,
            "comodos": [comodo.to_dict() for comodo in self.comodos],
            "num_comodos": list(self.num_comodos)
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> Self:
        return cls(
            nome_regiao=d["nome_regiao"],
            xy=tuple(d['xy']),
            tipo=d.get("tipo", "residencia"),
            tipo_data=d.get("tipo_data", {}),
            comodos=[Comodo.from_dict(comodo) for comodo in d.get("comodos", [])],
            num_comodos=tuple(d['num_comodos'])
        )
    
    @classmethod
    def lugar_padrao(cls,nome_regiao:str,xy:tuple[int,int],tipo:str) -> Self:
        inst=cls(
            nome_regiao=nome_regiao,
            xy=xy,
            tipo="",
            comodos=[
                Comodo(
                    (0,0),
                    "comodo_generico"
                )
            ]
        )
        inst.calcular_grid
        return inst
    
    @classmethod
    def residencia(cls,nome_regiao:str,xy:tuple[int,int]) -> Self:
        inst=cls(
            nome_regiao=nome_regiao,
            xy=xy,
            tipo="residencia",
            comodos=[
                Comodo(
                    (0,0),
                    "sala",
                    trancado=True
                ),
                Comodo(
                    (1,0),
                    "quarto"
                )
            ]
        )
        inst.calcular_grid
        return inst
