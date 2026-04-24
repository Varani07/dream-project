from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static, Button, Input, DataTable, Tree
from textual.screen import Screen, ModalScreen
from textual.containers import Grid, Horizontal, Vertical
from textual import on

from core.npc.npc import Npc
from core.world.world import World

from data.save_manager import salvar_jogo
from data.load_manager import get_saves, load_game

from utils.tempo import formato_data, formato_datetime

import shutil
from pathlib import Path


class ConfirmDialog(ModalScreen[bool]):
    def __init__(self, conteudo:str, positiva:str="Sim", negativa:str="Não") -> None:
        super().__init__()
        self.conteudo = conteudo
        self.positiva = positiva
        self.negativa = negativa

    def compose(self):
        yield Vertical(
            Static(self.conteudo),
            formatar_botao(Button(self.positiva, id="yes")),
            formatar_botao(Button(self.negativa, id="no"))
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)


class BaseScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield from self.compose_body()
        yield Footer()

    def compose_body(self) -> ComposeResult:
        yield from ()


class GameRunning(BaseScreen):
    BINDINGS = [
        ("d", "toogle_dark", "Toggle dark mode"), 
        ("q", "sair", "Sair"),
        ("h", "home", "Home"),
        ("m", "mapa", "Mapa"),
        ("s", "save", "Salvar")
    ]

    def __init__(self, mundo:World):
        super().__init__()
        self.world = mundo
        self.player = self.world.main_player()
        nome_regiao = self.player.info_local_atual.nome_regiao # type: ignore
        for regiao in self.world.regioes:
            if nome_regiao == regiao.nome:
                self.regiao = regiao
                break
        self.locais = {local.xy: local for local in self.regiao.locais}

    def compose_body(self):
        self.mapa = MiniMapa(self.regiao.num_locais, [loc for loc in self.player.get_locais_conhecidos.keys()], self.player.local_atual) # type: ignore
        self.info = Info(self.player, "player")
        self.barra = Horizontal(
            formatar_botao(Button("Player", id="player"))
        )
        self.barra.styles.height = 3
        
        yield Vertical(
            Horizontal(
                self.mapa,
                self.info
            ),
            self.barra
        )

    def action_mapa(self) -> None:
        self.info.atualizar(self.world, "mundo")

    def action_save(self) -> None:
        self.notify("Salvando jogo...")
        salvar_jogo(self.world) # type: ignore
        self.notify("Jogo salvo!")

    def on_button_pressed(self, event):
        if event.button.id.startswith("cell"):
            _, x, y = event.button.id.split("_")
            x = int(x)
            y = int(y)

            self.local = self.locais.get((x,y))

            pos_antiga = self.player.local_atual
            self.player.alternar_local(self.local)
            pos_nova = self.player.local_atual

            botao_antigo = self.query_one(f"#cell_{pos_antiga[0]}_{pos_antiga[1]}") # type: ignore
            botao_novo = self.query_one(f"#cell_{pos_nova[0]}_{pos_nova[1]}") # type: ignore

            if pos_antiga in [loc for loc in self.player.get_locais_conhecidos.keys()]:
                botao_antigo.label = "[blue]*[/]" # type: ignore
            else:
                botao_antigo.label = "o" # type: ignore

            botao_novo.label = "[red]x[/]" # type: ignore

            self.info.atualizar(self.local, "local")
        elif event.button.id == "player":
            self.info.atualizar(self.player, "player")
        

class Info(DataTable):
    def __init__(self, obj, tipo_obj):
        super().__init__()
        self.obj = obj
        self.tipo_obj = tipo_obj

    def on_mount(self):
        self.add_columns("Atributo", "Valor")
        self.atualizar(self.obj, self.tipo_obj)

    def atualizar(self, obj, tipo_obj):
        self.clear()

        if tipo_obj not in ["mundo", "local"]:
            match tipo_obj:
                case "player":
                    dict_obj = {
                        "nome": ["[blue]Nome[/]", 1], 
                        "nivel": ["[blue]Nivel[/]", 1], 
                        "npc": ["[blue]NPC[/]", 1],
                        "dinheiro": ["[blue]Dinheiro[/]", 1],
                        "energia": ["[green]Energia[/]", 2], 
                        "exp": ["[green]Exp[/]", 2],
                        "fome": ["[yellow]Fome[/]", 1], 
                        "sede": ["[yellow]Sede[/]", 1], 
                        "fadiga": ["[red]Fadiga[/]", 1], 
                        "sorte": ["[cyan]Sorte[/]", 1], 
                        "forca": ["[cyan]Força[/]", 1], 
                        "fit": ["[cyan]Fit[/]", 1]
                    }
            for chave, valor in dict_obj.items(): # type: ignore
                match valor[1]:
                    case 1:
                        atributo = getattr(obj, chave)
                        self.add_row(valor[0], str(atributo))
                    case 2:
                        atributo = getattr(obj, chave)
                        atributo_adc = getattr(obj, f"{chave}_cap")
                        self.add_row(valor[0], f"{atributo}/{atributo_adc}")
        else:
            match tipo_obj:
                case "mundo":
                    self.add_row("Nome", obj.nome)
                    for regiao in obj.regioes:
                        for local in regiao.locais:
                            self.add_row(f"{regiao.nome} {local.xy}", local.__class__.__name__)
                case "local":
                    self.add_row(f"Local {obj.xy}", obj.__class__.__name__)


class MiniMapa(Grid):
    def __init__(self, xy, pontos_conhecidos, localizacao_atual):
        super().__init__()
        self.xy = xy
        self.localizacao_atual = localizacao_atual
        self.pontos_conhecidos = pontos_conhecidos
        self.styles.grid_size_columns = xy[0]
        self.styles.grid_size_rows = xy[1]
        self.styles.grid_columns = ("6 " * xy[0]).strip()
        self.styles.grid_rows = ("3 " * xy[1]).strip()

    def compose(self):
        for y in range(self.xy[1]):
            for x in range(self.xy[0]):
                if (x,y) == self.localizacao_atual:
                    botao = Button("[red]x[/]", id=f"cell_{x}_{y}")
                elif (x,y) in self.pontos_conhecidos:
                    botao = Button("[blue]*[/]", id=f"cell_{x}_{y}")
                else:
                    botao = Button("o", id=f"cell_{x}_{y}")
                yield formatar_botao(botao)


class CriarPlayer(BaseScreen):
    def __init__(self):
        super().__init__()

    def compose_body(self):
        yield Input(placeholder="Player: ", max_length=25)

    def on_input_submitted(self, event: Input.Submitted):
        nome = event.value.strip()
        if len(nome) < 3:
            self.notify("Nome precisa ter pelo menos 3 caracteres!")
        else:
            world = World.mundo_inicial(Npc(nome))
            self.app.push_screen(GameRunning(world))


class LoadGame(BaseScreen):
    def __init__(self, saves):
        super().__init__()                                                    
        self.saves = saves

    def compose_body(self):
        yield formatar_tree(Tree("Saves", id="tree"))

    def on_mount(self) -> None:
        self.build_tree()

    def build_tree(self) -> None:
        self.dicio = {}
        self.children_saves = {}

        tree = self.query_one('#tree', Tree)
        tree.clear()
        root = tree.root
        self.build_tree_nodes(root)
        root.expand_all()

    def build_tree_nodes(self, root) -> None:
        for game_name, game in self.saves.items():
            node_a = root.add(game_name)
            self.children_saves[game_name] = {}
            for save_name, meta in sorted(game.items(), key=lambda x: formato_datetime(x[0]), reverse=False):
                self.children_saves[game_name][save_name] = []
                if meta['parent'] == "None":
                    node_b = node_a.add(formato_data(save_name))
                else:
                    node_pai = self.dicio[meta['parent']]
                    node_b = node_pai.add(formato_data(save_name))
                    self.children_saves[game_name][meta['parent']].append(save_name)
                node_b.add(f"[green]Player: {meta['player']}[/]", data={"game": game_name, "save": save_name})
                node_b.add(f"Nível: {meta['nivel']}")
                node_b.add(f"Local: {meta['local']}")
                node_b.add("[red]Deletar save[/]", data={"game": game_name, "save": save_name})
                node_saves = node_b.add("Saves")
                self.dicio[save_name] = node_saves

    @on(Tree.NodeSelected)
    def on_tree_node_selected(self, event: Tree.NodeSelected):
        node = event.node
        data = node.data
        if data:
            game = data['game']
            save = data['save']
            if str(node.label) == "Deletar save":
                def resposta(result:bool):
                    if result:
                        save_and_children = self.children_saves[game]
                        def apagar_saves(nome_save:str, children:list):
                            for child in children:
                                apagar_saves(child, save_and_children.get(child, []))
                            shutil.rmtree(f"data/saves/{game}/{nome_save}")
                        apagar_saves(save, save_and_children[save])
                    if not any(Path(f"data/saves/{game}").iterdir()):
                        shutil.rmtree(f"data/saves/{game}")
                    self.saves = get_saves()
                    self.build_tree()
                self.app.push_screen(ConfirmDialog("Deseja deletar save? (Deleta todos os saves subsequentes)"), resposta) # type: ignore
            else:
                self.notify("Carregando save...")
                load_save = load_game(game, save)
                self.app.push_screen(GameRunning(load_save))
                self.notify("Save carregado.")


class MenuInicial(BaseScreen):
    def compose_body(self):
        yield formatar_botao(Button("Novo Jogo", id="new_game"))
        yield formatar_botao(Button("Carregar Jogo", id="load_game"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "new_game":
            self.app.push_screen(CriarPlayer())
        elif event.button.id == "load_game":
            saves = get_saves()
            if len(saves) < 1:
                self.notify("Nenhum save disponível.")
            else:
                self.app.push_screen(LoadGame(saves))


class GameApp(App):
    BINDINGS = [
        ("d", "toogle_dark", "Toggle dark mode"), 
        ("h", "home", "Home"),
        ("q", "sair", "Sair")
    ]

    def action_toogle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_sair(self) -> None:
        self.app.exit()

    def action_home(self) -> None:
        self.app.push_screen(MenuInicial())

    def on_mount(self) -> None:
        self.push_screen(MenuInicial())


def formatar_botao(botao:Button) -> Button:
    botao.styles.background = "transparent"
    botao.can_focus = False
    return botao

def formatar_tree(tree:Tree) -> Tree:
    tree.can_focus = False
    return tree
