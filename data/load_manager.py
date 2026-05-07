from datetime import datetime
from pathlib import Path
from typing import Type

from core.world.world import World
from core.world.region import Region
from core.entity.entity import Entity, Component
from core.entity import components as comps_module
from utils.files import read_json


SCHEMA_ATUAL = 1
_MODULOS_COMPONENTES = (comps_module,)


def list_saves(base_dir: Path = Path("data/saves")) -> dict[str, dict[str, dict]]:
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


def _migrate(meta: dict, world_data: dict, entities_data: list,
            current_version: int, latest_version: int) -> tuple[dict, dict, list]:
    while current_version < latest_version:
        next_version = current_version + 1
        current_version = next_version
    return meta, world_data, entities_data


def _component_from_dict(cls_name: str, data: dict) -> Component | None:
    cls: Type[Component] | None = None
    for module in _MODULOS_COMPONENTES:
        cls = getattr(module, cls_name, None)
        if cls is not None:
            break
    if cls is None:
        return None  

    if cls_name == "LocationComponent":
        data = {
            **data, 
            "xy":tuple(data["xy"]),
            "room":tuple(data["room"]) 
        }
    if cls_name == "WorldKnowledgeComponent":
        # dict[str,dict[str,list[list[int,int]]]]
        data = {
            **data,
            "known_locations":{
                ok: {
                    tuple(int(i) for i in ik.split(",")): [tuple(v) for v in iv]
                    for ik, iv in ov.items()
                }
                for ok, ov in data["known_locations"].items()
            }
        }

    try:
        return cls(**data)
    except Exception:
        return cls()


def _entity_from_dict(d: dict) -> Entity:
    e = Entity(d["name"], entity_id=d["id"])
    for cls_name, comp_data in d.get("components", {}).items():
        comp = _component_from_dict(cls_name, comp_data)
        if comp is not None:
            e.add(comp)
    return e

def load_game(world_id: str, save_timestamp: str, base_dir: Path = Path("data/saves")) -> World:
    
    save_dir = base_dir / world_id / save_timestamp
    meta = read_json(save_dir / "meta.json")
    world_data = read_json(save_dir / "world.json")
    entities_data = read_json(save_dir / "entities.json")

    version = meta.get("schema_version", 0)
    if version < SCHEMA_ATUAL:
        meta, world_data, entities_data = _migrate(
            meta, world_data, entities_data,
            current_version=version, latest_version=SCHEMA_ATUAL,
        )

    world = World(world_data["name"])
    world.id = world_data["id"]
    world.time = datetime.fromisoformat(world_data["time"])
    world.parent_save = save_timestamp
    for r_dict in world_data.get("regions", []):
        world.add_region(Region.from_dict(r_dict))
    for e_dict in entities_data:
        world.add_entity(_entity_from_dict(e_dict))
    return world
