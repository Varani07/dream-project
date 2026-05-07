from core.systems import _vitalidade
from core.dialogue.handlers import register_dialogue_handlers


def register_systems(world):
    _vitalidade.register(world)
    register_dialogue_handlers(world)


__all__ = [
    "register_systems"
]