from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer


class BaseScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(id="header")
        yield from self.compose_body()
        yield Footer(id="footer")

    def compose_body(self) -> ComposeResult:
        yield from ()
        