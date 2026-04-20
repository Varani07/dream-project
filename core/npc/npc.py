from random import randint as ri, choice as chc

import uuid


class Npc():
    def __init__(self, nome, npc:bool=True):
        self.id = str(uuid.uuid4())

        self.nome = nome
        self.nivel = 1
        self.npc = npc

        # com limite
        self.energia = ri(15, 30)
        self.energia_cap = 30 
        self.exp = 0
        self.exp_cap = 20

        # renda
        self.dinheiro = ri(50, 250)

        # alimentação
        self.fome = ri(20, 25)
        self.sede = ri(20, 25)

        # penalidades
        self.fadiga = False 

        # performance geral
        self.sorte = ri(1, 3)
        self.forca = ri(1, 5)
        self.fit = ri(1, 3) 

        self.itens = []

        # localidade 
        self.local_atual = None
        self.info_local_atual = None
        self.dentro_local = False
        self.locais_conhecidos = dict()

    def alternar_local(self, local):
        self.locais_conhecidos[local.nome_regiao].update({local.xy: local})
        self.info_local_atual = local
        self.local_atual = local.xy

    @property
    def get_locais_conhecidos(self):
        return self.locais_conhecidos[self.info_local_atual.nome_regiao] # type: ignore
