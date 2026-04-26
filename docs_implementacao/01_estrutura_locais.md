# Passo a Passo: Mundo, Regiões e Locais no Textual

Neste guia, mostramos como integrar a lógica do seu `World` e `Region` com a interface da biblioteca `textual`, renderizando os locais como células.

## 1. Arquitetura Lógica
Você já possui a separação, então as classes baseadas no core devem parecer com isso:

```python
class Local:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.discovered = False
        self.npcs_present = []

class Region:
    def __init__(self, name):
        self.name = name
        # Uma malha 3x3 de locais como exemplo
        self.grid = [[None for _ in range(3)] for _ in range(3)]

class World:
    def __init__(self):
        self.regions = []
        self.current_region = None
```

## 2. A Interface em Textual (Células)
No Textual, podemos usar o `Grid` para representar visualmente a região do mapa.

```python
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Static, Button

class LocalCell(Static):
    """Representa um Local específico na tela."""
    def __init__(self, local_data, **kwargs):
        super().__init__(**kwargs)
        self.local_data = local_data

    def compose(self) -> ComposeResult:
        # Se for descoberto, mostra o nome, se não, mostra "?"
        display_name = self.local_data.name if self.local_data.discovered else "???"
        yield Button(display_name, id=f"btn_{self.local_data.name}")

class MapGrid(Static):
    def compose(self) -> ComposeResult:
        # Puxaria os dados da Regiao Atual
        with Grid(id="region_grid"):
            # Exemplo fixo gerando células
            for i in range(9):
                # local_mockup = get_local_do_mundo()
                yield LocalCell(local_data=MockLocal(f"Local {i}"))
```

## 3. Estilizando como Malha
O arquivo CSS (`app.tcss`) faria com que essas células ficassem quadradas:
```css
#region_grid {
    layout: grid;
    grid-size: 3 3;
    grid-columns: 1fr;
    grid-rows: 1fr;
    border: solid white;
}

LocalCell {
    border: solid green;
    content-align: center middle;
}
```

## 4. Viajando entre as células
Ao clicar em um botão `LocalCell`, o jogo verifica se o Local é adjacente. Se for para um não descoberto, gasta X de energia e Tempo. Em seguida, chama o sistema de tempo (veja o guia 02).
