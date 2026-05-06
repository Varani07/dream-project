from textual.containers import Grid
from textual.widgets import Button

from core.entity.components import ConhecimentoMundoComponent, LocalizacaoComponent
from core.world import Regiao, Local


class MiniMapa(Grid):
    def __init__(
            self,regiao:Regiao,localizacao:LocalizacaoComponent,
            conhecimento_mundo:ConhecimentoMundoComponent,**kw):
        
        super().__init__(**kw)
        self.desenhando = False
        self.montar_informacoes(regiao,localizacao,conhecimento_mundo)

    def compose(self):
        for y in range(self.rows):
            for x in range(self.cols):
                yield Button(self._label(x, y), id=f"cell_{x}_{y}", classes="cell_btn")

    def _label(self, x: int, y: int) -> str:
        if not self.inside_local:
            lugar = self.regiao.get_local((x,y))
        else:
            lugar = self.local.get_comodo((x,y))
            
        if (x, y) == self.atual:
            return "[red]x[/]"
        if (x, y) in self.conhecidos and lugar:
            return f"[{lugar.cor}]{lugar.glyph}[/]"
        if not self.inside_local or (self.inside_local and (x,y) in self.comodos_possiveis):
            return "[dim]?[/]"
        else:
            return "[dim]░[/]"

    def atualizar(
            self, conhecidos: set[tuple[int, int]],
            atual: tuple[int, int]) -> None:
        
        self.conhecidos = conhecidos
        self.atual = atual
        
        celulas = self.query(".cell_btn")

        for btn in celulas:
            if btn.id is None:
                continue
            _,x_str,y_str=btn.id.split("_")
            x,y=int(x_str),int(y_str)
            btn.label = self._label(x, y) #type: ignore

    async def recriar_mapa(
            self,regiao:Regiao,localizacao:LocalizacaoComponent,
            conhecimento_mundo:ConhecimentoMundoComponent) -> None:
        
        if self.desenhando:
            return
        self.desenhando=True

        try:
            self.montar_informacoes(regiao,localizacao,conhecimento_mundo)

            await self.query(".cell_btn").remove()

            novos_botoes = []
            for y in range(self.rows):
                for x in range(self.cols):
                    novos_botoes.append(
                        Button(self._label(x, y), id=f"cell_{x}_{y}", classes="cell_btn")
                    )
            await self.mount(*novos_botoes)
        finally:
            self.desenhando=False

    def montar_informacoes(
            self,regiao:Regiao,localizacao:LocalizacaoComponent,
            conhecimento_mundo:ConhecimentoMundoComponent):
    
        self.regiao = regiao
        local = self.regiao.get_local(localizacao.xy)
        assert local is not None
        self.local:Local=local
        self.inside_local:bool=localizacao.dentro_local
        self.comodos_possiveis = set()

        if not localizacao.dentro_local:
            self.atual = localizacao.xy
            self.conhecidos = conhecimento_mundo.local_conhecido(self.regiao.nome)
            self.cols, self.rows = regiao.num_locais
        else:
            self.atual = localizacao.comodo
            self.conhecidos = conhecimento_mundo.comodo_conhecido(
                nome_regiao=self.regiao.nome,
                xy=localizacao.xy
            )
            self.cols, self.rows = self.local.num_comodos
            self.comodos_possiveis = self.local.possiveis_comodos

        self.styles.grid_size_columns = self.cols
        self.styles.grid_size_rows = self.rows
        self.styles.grid_columns = ("6 " * self.cols).strip()
        self.styles.grid_rows = ("3 " * self.rows).strip()