from dataclasses import dataclass, field
from typing import Self

TIPOS_COMODO: dict[str, dict] = {
    "sala": {"glyph": "*", "cor": "white", "descricao": "Uma sala comum."},
    "quarto": {"glyph": "@", "cor": "yellow", "descricao": "Um quarto comum."},
    "comodo_generico": {"glyph": "0", "cor": "orange", "descricao": "Um lugar comum."}
}


@dataclass
class Comodo:
    xy: tuple[int, int]
    tipo: str = "quarto"
    tipo_data: dict = field(default_factory=dict)
    trancado: bool = False

    @property
    def descricao(self) -> str:
        return TIPOS_COMODO.get(self.tipo, {}).get("descricao", "Um lugar comum.")
    
    @property
    def glyph(self) -> str:
        return TIPOS_COMODO.get(self.tipo, {}).get("glyph", "?")
    
    @property
    def cor(self)->str:
        return TIPOS_COMODO.get(self.tipo, {}).get("cor", "white")
    
    def to_dict(self) -> dict:
        return {
            "xy": list(self.xy),
            "tipo": self.tipo,
            "tipo_data": self.tipo_data,
            "trancado": self.trancado
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> Self:
        return cls(
            xy=tuple(d['xy']),
            tipo=d.get("tipo", "residencia"),
            tipo_data=d.get("tipo_data", {}),
            trancado=d.get("trancado", False)
        )
