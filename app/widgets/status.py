from textual.widgets import Static

from core.entity.entity import Entity
from core.entity.components import VitalidadeComponent, LocalizacaoComponent


def _bar(valor: int, cap: int, largura: int = 10, cor: str = "green") -> str:
    if cap <= 0:
        return f"[{cor}]{'░' * largura}[/]"
    fill = max(0, min(largura, valor * largura // cap))
    return f"[{cor}]{'█' * fill}{'░' * (largura - fill)}[/] {valor}/{cap}"


class PainelStatus(Static):
    def __init__(self, player: Entity, **kw):
        super().__init__("", **kw)
        self.player = player

    def atualizar(self, player: Entity, tempo_str: str = "", local_nome: str = "") -> None:
        self.player = player
        self.linhas = [f"[b cyan]{player.nome}[/]"]

        self._vitalidade

        loc = player.get(LocalizacaoComponent)
        if loc:
            ar = "dentro" if loc.dentro_local else "fora"
            nome = local_nome or loc.regiao_nome
            self.linhas.append(f"[dim]📍 {nome} ({ar})[/]")

        if tempo_str:
            self.linhas.append(f"[dim]🕘 {tempo_str}[/]")

        self.update("\n".join(self.linhas))

    @property
    def _vitalidade(self) -> None:
        v = self.player.get(VitalidadeComponent)
        if v:
            cor = (
                "red" if v.energia <= v.energia_cap // 4
                else "yellow" if v.energia <= v.energia_cap // 2
                else "green"
            )
            self.linhas.append(f"[{cor}]❤ Energia[/] {_bar(v.energia, v.energia_cap, cor=cor)}")
