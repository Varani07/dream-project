from random import choices

import core.world.local as l


class Regiao():
    def __init__(self, nome_mundo:str) -> None:
        self.nome = ""
        self.nome_mundo = nome_mundo
        self.possibilidades = []
        self.locais = []

    def gerar_locais(self, tamanho:tuple[int, int]=(6, 5)) -> None:
        self.num_locais = tamanho
        for x in range(tamanho[0]):
            for y in range(tamanho[1]):
                local = choices([item[0] for item in self.possibilidades], weights=[peso[1] for peso in self.possibilidades], k=1)[0]
                self.locais.append(local(self.nome, (x, y)))
        
    @classmethod
    def cidade_inicial(cls, nome_mundo:str):
        inst = cls(nome_mundo)
        inst.nome = "Cidade Inicial"
        inst.possibilidades = [(l.Apartamento, 1), (l.Loja, 2), (l.Residencia, 4)]
        inst.gerar_locais()
        return inst
    