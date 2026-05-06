from core.systems import _vitalidade
from core.dialogue.handlers import registrar_handlers_dialogo


def registrar_sistemas(world):
    _vitalidade.registrar(world)
    registrar_handlers_dialogo(world)


__all__ = [
    "registrar_sistemas"
]