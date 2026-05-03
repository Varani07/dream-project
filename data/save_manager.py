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

    # `meta.json` é o resumo barato — UI lê só isso para popular a lista
    # de saves. Não inclua nada caro de calcular aqui.
    player = world.main_player()
    player_nome = player.nome if player else "—"
    player_local_tipo = "—"
    if player:
        loc = player.get(LocalizacaoComponent)
        if loc:
            regiao = world.get_regiao(loc.regiao_nome)
            local = regiao.get_local(loc.xy) if regiao else None
            if local:
                player_local_tipo = local.tipo

    meta = {
        "schema_version": SCHEMA_VERSION,
        "parent": world.parent_save,           # rastreia árvore de saves
        "player": player_nome,
        "local_tipo": player_local_tipo,
        "tempo": world.tempo.isoformat(),       # datetime -> string ISO
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

    # Próximo save terá este como pai.
    world.parent_save = timestamp
    return timestamp
