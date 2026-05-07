from textual.widgets import Static, Button, Input
from textual.containers import Vertical

from app.screens.base import BaseScreen
from core.factory import new_world


class NewGame(BaseScreen):
    def compose_body(self):
        yield Vertical(
            Static("Crie seu personagem", id="new_title"),
            Static("[dim]Você pode trocar de protagonista mais tarde.[/]"),
            Input(placeholder="Nome do personagem", max_length=25, id="input_name"),
            Button("Iniciar", id="start"),
            Button("Voltar",  id="back"),
            id="new_game_container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start":
            self._start()
        elif event.button.id == "back":
            self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._start()

    def _start(self) -> None:
        name_input = self.query_one("#input_name", Input)
        name = name_input.value.strip()
        if len(name) < 3:
            self.notify("Nome precisa ter pelo menos 3 caracteres.", severity="warning")
            return
        from app.screens.game import GameRunning
        world = new_world(name)
        self.app.push_screen(GameRunning(world))
