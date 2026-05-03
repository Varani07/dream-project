from dataclasses import dataclass, field
from typing import Self

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
    trancado: bool = False

    @property
    def descricao(self) -> str:
        return TIPOS_LOCAL.get(self.tipo, {}).get("descricao", "Um lugar comum.")
    
    @property
    def glyph(self) -> str:
        return TIPOS_LOCAL.get(self.tipo, {}).get("glyph", "?")
    
    def to_dict(self) -> dict:
        return {
            "nome_regiao": self.nome_regiao,
            "xy": list(self.xy),
            "tipo": self.tipo,
            "tipo_data": self.tipo_data,
            "trancado": self.trancado
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> Self:
        return cls(
            nome_regiao=d["nome_regiao"],
            xy=tuple(d['xy']),
            tipo=d.get("tipo", "residencia"),
            tipo_data=d.get("tipo_data", {}),
            trancado=d.get("trancado", False)
        )
