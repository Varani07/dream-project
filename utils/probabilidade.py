from random import randint as ri
from dataclasses import dataclass

ESCALA = 1000

@dataclass
class Modificador:
    valor: float
    aumenta: bool

def probabilidade(porcentagem: int, fadiga: bool, dado: int = 10, **kwargs: Modificador) -> bool:
    num_aleatorio = ri(1, ESCALA)
    fator_dado = (dado - 10) * (ESCALA // 100)
    porcentagem = porcentagem * (ESCALA // 100) + fator_dado
    for mod in kwargs.values():
        if mod.aumenta:
            if not fadiga:
                porcentagem += int(mod.valor * (ESCALA // 100))
        else:
            porcentagem -= int(mod.valor * (ESCALA // 100))
    if fadiga:
        porcentagem -= 30 * (ESCALA // 100)
    return porcentagem >= num_aleatorio
        