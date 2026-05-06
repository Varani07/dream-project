from textual.widgets import Static, Button, Input
from textual.containers import Vertical

from app.screens.base import BaseScreen
from core.factory import novo_mundo


class NovoJogo(BaseScreen):
    def compose_body(self):
        yield Vertical(
            Static("Crie seu personagem", id="titulo_novo"),
            Static("[dim]Você pode trocar de protagonista mais tarde.[/]"),
            Input(placeholder="Nome do personagem", max_length=25, id="input_nome"),
            Button("Iniciar", id="iniciar"),
            Button("Voltar",  id="voltar"),
            id="novo_jogo_container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "iniciar":
            self._iniciar()
        elif event.button.id == "voltar":
            self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._iniciar()

    def _iniciar(self) -> None:
        nome_input = self.query_one("#input_nome", Input)
        nome = nome_input.value.strip()
        if len(nome) < 3:
            self.notify("Nome precisa ter pelo menos 3 caracteres.", severity="warning")
            return
        from app.screens.game import GameRunning
        world = novo_mundo(nome)
        self.app.push_screen(GameRunning(world))
