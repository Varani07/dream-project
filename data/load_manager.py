from datetime import datetime
from pathlib import Path
from typing import Type

from core.world.world import World
from core.world.regiao import Regiao
from core.entity.entity import Entity, Component
from core.entity import components as comps_module
from utils.files import read_json


SCHEMA_ATUAL = 1
_MODULOS_COMPONENTES = (comps_module,)


def listar_saves(base_dir: Path = Path("data/saves")) -> dict[str, dict[str, dict]]:
    out: dict[str, dict[str, dict]] = {}
    if not base_dir.exists():
        return out
    for world_dir in base_dir.iterdir():
        if not world_dir.is_dir():
            continue
        for save_dir in world_dir.iterdir():
            meta_file = save_dir / "meta.json"
            if meta_file.exists():
                out.setdefault(world_dir.name, {})[save_dir.name] = read_json(meta_file)
    return out


def _migrar(meta: dict, world_data: dict, entities_data: list,
            de: int, para: int) -> tuple[dict, dict, list]:
    while de < para:
        proximo = de + 1
        de = proximo
    return meta, world_data, entities_data


def _component_from_dict(cls_name: str, data: dict) -> Component | None:
    cls: Type[Component] | None = None
    for modulo in _MODULOS_COMPONENTES:
        cls = getattr(modulo, cls_name, None)
        if cls is not None:
            break
    if cls is None:
        return None  

    if cls_name == "LocalizacaoComponent" and "xy" in data:
        data = {**data, "xy": tuple(data["xy"])}

    try:
        return cls(**data)
    except Exception:
        return cls()


def _entity_from_dict(d: dict) -> Entity:
    e = Entity(d["nome"], entity_id=d["id"])
    for cls_name, comp_data in d.get("components", {}).items():
        comp = _component_from_dict(cls_name, comp_data)
        if comp is not None:
            e.add(comp)
    return e


def carregar_jogo(world_id: str, save_timestamp: str, base_dir: Path = Path("data/saves")) -> World:
    save_dir = base_dir / world_id / save_timestamp
    meta = read_json(save_dir / "meta.json")
    world_data = read_json(save_dir / "world.json")
    entities_data = read_json(save_dir / "entities.json")

    versao = meta.get("schema_version", 0)
    if versao < SCHEMA_ATUAL:
        meta, world_data, entities_data = _migrar(
            meta, world_data, entities_data,
            de=versao, para=SCHEMA_ATUAL,
        )

    world = World(world_data["nome"])
    world.id = world_data["id"]
    world.tempo = datetime.fromisoformat(world_data["tempo"])
    world.parent_save = save_timestamp
    for r_dict in world_data.get("regioes", []):
        world.add_regiao(Regiao.from_dict(r_dict))
    for e_dict in entities_data:
        world.add_entity(_entity_from_dict(e_dict))
    return world
