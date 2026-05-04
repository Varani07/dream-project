from textual.app import App

from ui.screens.menu import MenuInicial


class GameApp(App):
    CSS_PATH = "styles/app.tcss"
    TITLE = "Dream Project"
    SUB_TITLE = "RPG textual de mundo vivo"

    def action_home(self) -> None:
        self.push_screen(MenuInicial())

    def action_sair(self) -> None:
        self.exit()

    def on_mount(self) -> None:
        self.push_screen(MenuInicial())
        