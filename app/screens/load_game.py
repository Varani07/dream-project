
from textual.widgets import Tree, Button
from textual.containers import Vertical
from textual import on

from app.screens.base import BaseScreen
from data import load_game, list_saves, delete_save
from utils.time import datetime_format, date_format


class LoadGame(BaseScreen):
    def __init__(self, saves: dict[str, dict[str, dict]]) -> None:
        super().__init__()
        self.saves = saves

    def compose_body(self):
        yield Vertical(
            Tree("Saves", id="tree_saves"),
            Button("Voltar", id="back"),
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
        for world_id, world_saves in self.saves.items():
            world_node = root.add(f"Mundo {world_id}")
            for timestamp, meta in sorted(world_saves.items(), key=lambda x: datetime_format(x[0]), reverse=False):
                if meta['parent'] is None:
                    save_node = world_node.add(f"{date_format(timestamp)} - {meta['player']}")
                else:
                    parent_node = self._parent_nodes[meta['parent']]
                    save_node = parent_node.add(f"{date_format(timestamp)} - {meta['player']}")
                save_node.add(f"[green]Player: {meta['player']}[/]", data={"game": world_id, "save": timestamp, "action": "load"})
                save_node.add(f"Local: {str(meta['location_type']).capitalize()}")
                save_node.add(f"[red]Deletar save[/]", data={"game": world_id, "save": timestamp, "action": "delete"})
                saves_node = save_node.add("Saves")
                self._parent_nodes[timestamp] = saves_node

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()

    @on(Tree.NodeSelected)
    def _on_node_selected(self, event: Tree.NodeSelected) -> None:
        data = event.node.data
        if not data:
            return
        if data["action"] == "load":
            try:
                world = load_game(data["game"], data["save"])
            except Exception as e:
                self.notify(f"Falha ao carregar: {e}", severity="error")
                return
            from app.screens.game import GameRunning
            self.app.push_screen(GameRunning(world))
        elif data["action"] == "delete":
            removed_saves = delete_save(data["game"], data["save"])
            self.saves = list_saves()
            self._build_tree()
            self.notify(f"{len(removed_saves)} save(s) apagado(s).")