from core.world.world import World
from core.world.regiao import Regiao
from core.world import local as l
from core.npc.npc import Npc

from utils.tempo import formato_save
from utils.file_management import save_write_json

from datetime import datetime
from pathlib import Path

def salvar_jogo(jogo:World) -> None:
    agora = formato_save(datetime.now())
    BASE_PATH = Path(f"data/saves/{jogo.id}/{agora}")
    (BASE_PATH).mkdir(parents=True, exist_ok=True)

    regioes = []
    residencias = []
    apartamentos = []
    lojas = []
    npcs = []

    def dict_to_file(conteudo:dict|list, nome_arquivo:str) -> None:
        path = (BASE_PATH/nome_arquivo)
        save_write_json(path, "w", conteudo)

    def meta(id:str, parente:str|None) -> None:
        dicio = dict()
        dicio['id'] = id
        dicio['parent'] = str(parente)

        player = jogo.main_player()
        dicio['player'] = player.nome
        dicio['nivel'] = player.nivel
        dicio['local'] = player.info_local_atual.__class__.__name__

        dict_to_file(dicio, "meta.json")

    def to_dict(obj, retorno=False):
        dicio = dict()
        if isinstance(obj, World):
            dicio['id'] = obj.id
            dicio['nome'] = obj.nome
            for regiao in obj.regioes:
                to_dict(regiao)
            for npc in obj.npcs:
                to_dict(npc)
            dicio['ano'] = obj.tempo.year
            dicio['mes'] = obj.tempo.month
            dicio['dia'] = obj.tempo.day
            dicio['hora'] = obj.tempo.hour
            dicio['minuto'] = obj.tempo.minute

            meta(agora, obj.parent)
            dict_to_file(dicio, "world.json")
        elif isinstance(obj, Regiao):
            dicio['nome'] = obj.nome
            dicio['nome_mundo'] = obj.nome_mundo
            dicio['possibilidades'] = [(possibilidade[0].__name__, possibilidade[1]) for possibilidade in obj.possibilidades]
            dicio['num_locais'] = obj.num_locais
            regioes.append(dicio)
            for local in obj.locais:
                to_dict(local)
        elif isinstance(obj, l.Residencia):
            dicio['nome_regiao'] = obj.nome_regiao
            dicio['xy'] = obj.xy
            if retorno:
                return dicio
            residencias.append(dicio)
        elif isinstance(obj, l.Apartamento):
            dicio['nome_regiao'] = obj.nome_regiao
            dicio['xy'] = obj.xy
            if retorno:
                return dicio
            apartamentos.append(dicio)
        elif isinstance(obj, l.Loja):
            dicio['nome_regiao'] = obj.nome_regiao
            dicio['xy'] = obj.xy
            if retorno:
                return dicio
            lojas.append(dicio)
        elif isinstance(obj, Npc):
            dicio['id'] = obj.id
            dicio['nome'] = obj.nome
            dicio['nivel'] = obj.nivel
            dicio['npc'] = obj.npc
            dicio['energia'] = obj.energia
            dicio['energia_cap'] = obj.energia_cap
            dicio['exp'] = obj.exp
            dicio['exp_cap'] = obj.exp_cap
            dicio['dinheiro'] = obj.dinheiro
            dicio['fome'] = obj.fome
            dicio['sede'] = obj.sede
            dicio['fadiga'] = obj.fadiga
            dicio['sorte'] = obj.sorte
            dicio['forca'] = obj.forca
            dicio['fit'] = obj.fit
            dicio['local_atual'] = obj.local_atual
            dicio['dentro_local'] = obj.dentro_local
            dicio['info_local_atual'] = to_dict(obj.info_local_atual, True)
            dicio['locais_conhecidos'] = [
                to_dict(lc, True)
                for local_conhecido in obj.locais_conhecidos.values()
                for lc in local_conhecido.values()
            ]
            npcs.append(dicio)

    to_dict(jogo)
    jogo.parent = agora # type: ignore

    if len(regioes) > 0:
        dict_to_file(regioes, "regioes.json")
    if len(residencias) > 0:
        dict_to_file(residencias, "residencias.json")
    if len(apartamentos) > 0:
        dict_to_file(apartamentos, "apartamentos.json")
    if len(lojas) > 0:
        dict_to_file(lojas, "lojas.json")
    if len(npcs) > 0:
        dict_to_file(npcs, "npcs.json")
