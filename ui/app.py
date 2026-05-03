class GameApp(App):
    CSS_PATH = "styles/app.tcss"
    def on_mount(self) -> None:
        self.push_screen(MenuInicial())