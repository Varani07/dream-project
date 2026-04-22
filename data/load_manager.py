from core.world.world import World
from core.world.regiao import Regiao
from core.world import local as l
from core.npc.npc import Npc

from utils.tempo import formato_save
from utils.file_management import save_write_json, get_json_files

from datetime import datetime
from pathlib import Path
import json


def load_game(game:str, save:str) -> World:
    json_files = get_json_files(Path(f"data/saves/{game}/{save}"))
    

    world = World("teste")
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
