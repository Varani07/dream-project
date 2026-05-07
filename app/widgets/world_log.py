from textual.widgets import RichLog


class WorldLog(RichLog):

    def __init__(self, **kw):
        super().__init__(
            highlight=False, 
            markup=True,    
            wrap=True, 
            max_lines=2000, 
            auto_scroll=True,
            **kw,
        )

    def add_event(self, text: str) -> None:
        self.write(text)