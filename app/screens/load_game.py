
from textual.widgets import Tree, Button
from textual.containers import Vertical
from textual import on

from app.screens.base import BaseScreen
from data import carregar_jogo, listar_saves, apagar_save
from utils.tempo import formato_datetime, formato_data


class LoadGame(BaseScreen):
    def __init__(self, saves: dict[str, dict[str, dict]]) -> None:
        super().__init__()
        self.saves = saves

    def compose_body(self):
        yield Vertical(
            Tree("Saves", id="tree_saves"),
            Button("Voltar", id="voltar"),
            id="load_container",
        )

    def on_mount(self) -> None:
        self._build_tree()

    def _build_tree(self) -> None:
        self._parent_nodes = {}

        tree = self.query_one("#tree_saves", Tree)
        tree.clear()
        root = tree.root
        self._build_tree_nodes(root)
        root.expand_all()

    def _build_tree_nodes(self, root) -> None:
        for world_id, saves_do_mundo in self.saves.items():
            mundo_node = root.add(f"Mundo {world_id}")
            for timestamp, meta in sorted(saves_do_mundo.items(), key=lambda x: formato_datetime(x[0]), reverse=False):
                if meta['parent'] is None:
                    save_node = mundo_node.add(f"{formato_data(timestamp)} - {meta['player']}")
                else:
                    parent_node = self._parent_nodes[meta['parent']]
                    save_node = parent_node.add(f"{formato_data(timestamp)} - {meta['player']}")
                save_node.add(f"[green]Player: {meta['player']}[/]", data={"game": world_id, "save": timestamp, "acao": "carregar"})
                save_node.add(f"Local: {str(meta['local_tipo']).capitalize()}")
                save_node.add(f"[red]Deletar save[/]", data={"game": world_id, "save": timestamp, "acao": "apagar"})
                saves_node = save_node.add("Saves")
                self._parent_nodes[timestamp] = saves_node

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "voltar":
            self.app.pop_screen()

    @on(Tree.NodeSelected)
    def _on_node_selected(self, event: Tree.NodeSelected) -> None:
        data = event.node.data
        if not data:
            return
        if data["acao"] == "carregar":
            try:
                world = carregar_jogo(data["game"], data["save"])
            except Exception as e:
                self.notify(f"Falha ao carregar: {e}", severity="error")
                return
            from app.screens.game import GameRunning
            self.app.push_screen(GameRunning(world))
        elif data["acao"] == "apagar":
            removidos = apagar_save(data["game"], data["save"])
            self.saves = listar_saves()
            self._build_tree()
            self.notify(f"{len(removidos)} save(s) apagado(s).")