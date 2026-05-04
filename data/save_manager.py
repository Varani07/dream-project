from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path

from core.world.world import World
from core.entity.entity import Entity
from core.entity.components import LocalizacaoComponent
from utils.tempo import formato_save
from utils.files import write_json


SCHEMA_VERSION: int = 1
_COMPONENTES_TRANSIENTES: set[str] = set()


def _normalize_for_json(cls_name: str, data: dict) -> dict:
    if cls_name == "LocalizacaoComponent" and "xy" in data:
        return {**data, "xy": list(data["xy"])}
    return data

def _entity_to_dict(entity: Entity) -> dict:
    comps_dict: dict[str, dict] = {}
    for cls_name, comp in entity.all_components().items():
        if cls_name in _COMPONENTES_TRANSIENTES:
            continue
        if is_dataclass(comp):
            data = asdict(comp)
        else:
            data = dict(comp.__dict__)
        data = _normalize_for_json(cls_name, data)
        comps_dict[cls_name] = data
    return {
        "id": entity.id,
        "nome": entity.nome,
        "components": comps_dict,
    }

def salvar_jogo(world: World, base_dir: Path = Path("data/saves")) -> str:
    timestamp = formato_save(datetime.now())
    save_dir = base_dir / world.id / timestamp
    save_dir.mkdir(parents=True, exist_ok=True)

    player = world.main_player()
    assert player is not None
    if player:
        loc = player.get(LocalizacaoComponent)
        if loc:
            regiao = world.get_regiao(loc.regiao_nome)
            local = regiao.get_local(loc.xy) if regiao else None
            if local:
                player_local_tipo = local.tipo

    meta = {
        "schema_version": SCHEMA_VERSION,
        "parent": world.parent_save,           
        "player": player.nome,
        "local_tipo": player_local_tipo,
        "tempo": world.tempo.isoformat(),  
    }

    world_data = {
        "id": world.id,
        "nome": world.nome,
        "tempo": world.tempo.isoformat(),
        "regioes": [r.to_dict() for r in world.regioes],
    }

    entities_data = [_entity_to_dict(e) for e in world.entities]

    write_json(save_dir / "meta.json", meta)
    write_json(save_dir / "world.json", world_data)
    write_json(save_dir / "entities.json", entities_data)

    world.parent_save = timestamp
    return timestamp

def apagar_save(world_id: str, timestamp: str, base_dir: Path = Path("data/saves")) -> list[str]:
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

    filhos: dict[str | None, list[str]] = {}
    for ts, meta in metas.items():
        filhos.setdefault(meta.get("parent"), []).append(ts)

    a_remover: list[str] = []
    fila = [timestamp]
    while fila:
        atual = fila.pop()
        a_remover.append(atual)
        for f in filhos.get(atual, []):
            fila.append(f)

    for ts in a_remover:
        path = world_dir / ts
        if path.exists():
            shutil.rmtree(path)

    if world_dir.exists() and not any(world_dir.iterdir()):
        shutil.rmtree(world_dir)

    return a_remover
