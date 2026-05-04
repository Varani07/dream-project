from core.entity import criar_player
from core.world import World
from core.systems import registrar_sistemas


def novo_mundo(nome_player: str, nome_mundo: str = "Kazer"):
    player = criar_player(nome_player)
    world = World.mundo_inicial(player, nome_mundo)
    return world