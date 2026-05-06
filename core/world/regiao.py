from random import choices
from core.world.local import Local
from typing import Self


COMPOSICAO_CIDADE_INICIAL: list[tuple[str, int]] = [
    ("residencia", 4),
    ("loja", 2),
    ("taverna", 1),
    ("praca", 1)
]


class Regiao:
    def __init__(self, nome_mundo: str, nome: str = "") -> None:
        self.nome_mundo = nome_mundo
        self.nome = nome
        self.composicao: list[tuple[str, int]] = []
        self.locais: list[Local] = []
        self.num_locais: tuple[int, int] = (0, 0)

    def gerar_locais(self, tamanho: tuple[int, int] = (6, 5)) -> None:
        self.num_locais = tamanho
        tipos = [t[0] for t in self.composicao]
        pesos = [t[1] for t in self.composicao]
        for x in range(tamanho[0]):
            for y in range(tamanho[1]):
                tipo = choices(tipos, weights=pesos, k=1)[0]
                match tipo:
                    case 'residencia':
                        local = Local.residencia(self.nome,(x,y))
                    case _:
                        local = Local.lugar_padrao(self.nome,(x,y),tipo)
                self.locais.append(local)

    def get_local(self, xy: tuple[int, int]) -> Local | None:
        return next(
            (local for local in self.locais if local.xy == xy),
            None
        )
    
    @classmethod
    def cidade_inicial(cls, nome_mundo: str) -> Self:
        inst = cls(nome_mundo, nome="Cidade Inicial")
        inst.composicao = COMPOSICAO_CIDADE_INICIAL
        inst.gerar_locais()
        return inst
    
    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "nome_mundo": self.nome_mundo,
            "composicao": [list(t) for t in self.composicao],
            "num_locais": list(self.num_locais),
            "locais": [local.to_dict() for local in self.locais],
        }

    @classmethod
    def from_dict(cls, d: dict) -> Self:
        inst = cls(d["nome_mundo"], nome=d["nome"])
        inst.composicao = [tuple(t) for t in d.get("composicao", [])]
        inst.num_locais = tuple(d["num_locais"])
        inst.locais = [Local.from_dict(ld) for ld in d.get("locais", [])]
        return inst
    