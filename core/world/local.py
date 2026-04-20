class Local():
    def __init__(self, nome_regiao, xy):
        self.nome_regiao = nome_regiao
        self.xy = xy


class Residencia(Local):
    def __init__(self, nome_regiao, xy) -> None:
        super().__init__(nome_regiao, xy)


class Loja(Local):
    def __init__(self, nome_regiao, xy) -> None:
        super().__init__(nome_regiao, xy)


class Apartamento(Local):
    def __init__(self, nome_regiao, xy) -> None:
        super().__init__(nome_regiao, xy)
