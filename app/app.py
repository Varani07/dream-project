from textual.app import App

from app.screens.menu import MainMenu


class GameApp(App):
    CSS_PATH = "styles/app.tcss"
    TITLE = "Dream Project"
    SUB_TITLE = "RPG textual de mundo vivo"

    def action_home(self) -> None:
        self.push_screen(MainMenu())

    def action_exit(self) -> None:
        self.exit()

    def on_mount(self) -> None:
        self.push_screen(MainMenu())
        