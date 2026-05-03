from core.systems import _vitalidade


def registrar_sistemas(world):
    _vitalidade.registrar(world)


__all__ = [
    "registrar_sistemas"
]