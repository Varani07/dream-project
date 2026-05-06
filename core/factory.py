from core.entity import criar_player, criar_npc
from core.world import World
from core.systems import registrar_sistemas
from core.entity.components import LocalizacaoComponent


def novo_mundo(nome_player: str, nome_mundo: str = "Kazer"):
    player = criar_player(nome_player)
    world = World.mundo_inicial(player, nome_mundo)
    player_loc = player.get(LocalizacaoComponent)
    assert player_loc is not None

    bertrand = criar_npc(
        "Bertrand", arquetipo="rabugento",
        regiao_nome=nome_mundo,
        xy=player_loc.xy, dentro_local=True,
        c_xy=player_loc.comodo
    )
    world.add_entity(bertrand)

    return world