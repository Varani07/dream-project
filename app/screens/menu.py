from textual.widgets import Static, Button
from textual.containers import Vertical
from textual.app import ComposeResult

from app.screens.base import BaseScreen


class MainMenu(BaseScreen):
    def compose_body(self) -> ComposeResult:
        yield Vertical(
            Static("DREAM PROJECT", id="title"),
            Static("[dim]um RPG textual de mundo vivo[/]", id="subtitle"),
            Button("Novo Jogo",     id="new_game"),
            Button("Carregar Jogo", id="load_game"),
            Button("Sair",          id="exit_game"),
            id="menu_container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "new_game":
            from app.screens.new_game import NewGame 
            self.app.push_screen(NewGame())
        elif event.button.id == "load_game":
            from app.screens.load_game import LoadGame
            from data.load_manager import list_saves
            saves = list_saves()
            if not saves:
                self.notify("Nenhum save disponível.", severity="warning")
                return
            self.app.push_screen(LoadGame(saves))
        elif event.button.id == "exit_game":
            self.app.exit()
