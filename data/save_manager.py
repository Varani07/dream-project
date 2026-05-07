from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path

from core.world.world import World
from core.entity.entity import Entity
from core.entity.components import LocationComponent
from utils.time import save_format
from utils.files import write_json


SCHEMA_VERSION: int = 1
_TRANSIENT_COMPONENTS: set[str] = set()


def _normalize_for_json(cls_name: str, data: dict) -> dict:
    if cls_name == "WorldKnowledgeComponent":
        # dict[str,dict[tuple[int,int],list[tuple[int,int]]]]
        return {
            **data,
            "known_locations":{
                ok: {
                    f"{x},{y}": iv
                    for (x,y), iv in ov.items()
                }
                for ok, ov in data['known_locations'].items()
            }
        }
    return data

def _entity_to_dict(entity: Entity) -> dict:
    comps_dict: dict[str, dict] = {}
    for cls_name, comp in entity.all_components().items():
        if cls_name in _TRANSIENT_COMPONENTS:
            continue
        if is_dataclass(comp):
            data = asdict(comp)
        else:
            data = dict(comp.__dict__)
        data = _normalize_for_json(cls_name, data)
        comps_dict[cls_name] = data
    return {
        "id": entity.id,
        "name": entity.name,
        "components": comps_dict,
    }

def save_game(world: World, base_dir: Path = Path("data/saves")) -> str:
    timestamp = save_format(datetime.now())
    save_dir = base_dir / world.id / timestamp
    save_dir.mkdir(parents=True, exist_ok=True)

    player = world.main_player()
    assert player is not None
    if player:
        loc = player.get(LocationComponent)
        if loc:
            region = world.get_region(loc.region_name)
            location = region.get_location(loc.xy) if region else None
            if location:
                player_location_type = location.location_type

    meta = {
        "schema_version": SCHEMA_VERSION,
        "parent": world.parent_save,           
        "player": player.name,
        "location_type": player_location_type,
        "time": world.time.isoformat(),  
    }

    world_data = {
        "id": world.id,
        "name": world.name,
        "time": world.time.isoformat(),
        "regions": [r.to_dict() for r in world.regions],
    }

    entities_data = [_entity_to_dict(e) for e in world.entities]

    write_json(save_dir / "meta.json", meta)
    write_json(save_dir / "world.json", world_data)
    write_json(save_dir / "entities.json", entities_data)

    world.parent_save = timestamp
    return timestamp

def delete_save(world_id: str, timestamp: str, base_dir: Path = Path("data/saves")) -> list[str]:
    import shutil
    from utils.files import read_json

    world_dir = base_dir / world_id
    if not world_dir.exists():
        return []

    metas: dict[str, dict] = {}
    for save_dir in world_dir.iterdir():
        if not save_dir.is_dir():
            continue
        meta_file = save_dir / "meta.json"
        if meta_file.exists():
            try:
                metas[save_dir.name] = read_json(meta_file)
            except Exception:
                continue

    children: dict[str | None, list[str]] = {}
    for ts, meta in metas.items():
        children.setdefault(meta.get("parent"), []).append(ts)

    to_delete: list[str] = []
    queue = [timestamp]
    while queue:
        current = queue.pop()
        to_delete.append(current)
        for child in children.get(current, []):
            queue.append(child)

    for ts in to_delete:
        path = world_dir / ts
        if path.exists():
            shutil.rmtree(path)

    if world_dir.exists() and not any(world_dir.iterdir()):
        shutil.rmtree(world_dir)

    return to_delete
