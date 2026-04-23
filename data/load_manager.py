from core.world.world import World
from core.world.regiao import Regiao
from core.world import local as l
from core.npc.npc import Npc

from utils.tempo import formato_save
from utils.file_management import save_write_json, get_json_files

from datetime import datetime
from pathlib import Path
import importlib
import json

LOCAL_MODULE = importlib.import_module("core.world.local")


def load_game(game:str, save:str) -> World:
    json_files = get_json_files(Path(f"data/saves/{game}/{save}"))
    world = class_world(json_files['world.json'], save)
    class_regioes(json_files['regioes.json'], json_files['locais.json'], world)
    class_npcs(json_files['npcs.json'], world)
    return world

def get_saves() -> dict[str, dict[str, dict]]:
    pasta = Path("data/saves")
    dicio = {}

    for game in pasta.iterdir():
        for save in game.iterdir():
            file = save / "meta.json"
            if file.exists():
                dicio.setdefault(game.name, {})[save.name] = save_write_json(file, "r")
    return dicio

def class_world(world_dict:dict, save:str) -> World:
    world = World(world_dict['nome'])
    world.id = world_dict['id']
    world.tempo = datetime(world_dict['ano'], world_dict['mes'], world_dict['dia'], world_dict['hora'], world_dict['minuto'])
    world.parent = save # type: ignore
    return world

def class_regioes(regioes:dict, locais_dict:dict, world:World) -> None:
    for regiao_dict in regioes:
        regiao = Regiao(regiao_dict['nome_mundo'])
        regiao.nome = regiao_dict['nome']
        regiao.num_locais = tuple(regiao_dict['num_locais'])
        for possibilidade in regiao_dict['possibilidades']:
            regiao.possibilidades.append((getattr(LOCAL_MODULE, possibilidade[0]), possibilidade[1]))
        locais = locais_dict[regiao.nome]
        for local in locais:
            class_local(local, regiao)
        world.regioes.append(regiao)

def class_local(local_dict:dict, regiao:Regiao) -> None:
    classe = getattr(LOCAL_MODULE, local_dict['classe'])
    match local_dict['classe']:
        case "Residencia" | "Loja" | "Apartamento":
            local = classe(local_dict['nome_regiao'], tuple(local_dict['xy']))
            regiao.locais.append(local)

def class_npcs(npcs:dict, world:World) -> None:
    for npc_dict in npcs:
        npc = Npc(npc_dict['nome'], npc_dict['npc'])
        npc.id = npc_dict['id']
        npc.nivel = npc_dict['nivel']
        npc.energia = npc_dict['energia']
        npc.energia_cap = npc_dict['energia_cap']
        npc.exp = npc_dict['exp']
        npc.energia_cap = npc_dict['exp_cap']
        npc.dinheiro = npc_dict['dinheiro']
        npc.fome = npc_dict['fome']
        npc.sede = npc_dict['sede']
        npc.fadiga = npc_dict['fadiga']
        npc.sorte = npc_dict['sorte']
        npc.forca = npc_dict['forca']
        npc.fit = npc_dict['fit']
        npc.local_atual = tuple(npc_dict['local_atual'])
        npc.dentro_local = npc_dict['dentro_local']
        npc.info_local_atual = world.get_regiao(npc_dict['info_local_atual']['nome_regiao']).get_local(tuple(npc_dict['info_local_atual']['xy']))
        for local_conhecido in npc_dict['locais_conhecidos']:
            npc.locais_conhecidos.setdefault(local_conhecido['nome_regiao'], {}).update({tuple(local_conhecido['xy']): world.get_regiao(local_conhecido['nome_regiao']).get_local(tuple(local_conhecido['xy']))})
        world.npcs.append(npc)
