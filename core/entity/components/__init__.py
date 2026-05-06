from core.entity.components._identidade import (
    IdentidadeComponent,
    ControlePlayerComponent,
)
from core.entity.components._mundo import (
    LocalizacaoComponent, ConhecimentoMundoComponent
)
from core.entity.components._vitalidade import VitalidadeComponent
from core.entity.components._personalidade import (
    AfinidadeComponent, 
    PersonalidadeComponent,
    ARQUETIPOS_VALIDOS
)


__all__ = [
    "IdentidadeComponent", "ControlePlayerComponent",
    "LocalizacaoComponent", "ConhecimentoMundoComponent",
    "VitalidadeComponent",
    "AfinidadeComponent", "PersonalidadeComponent", "ARQUETIPOS_VALIDOS"
]
