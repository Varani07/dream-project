from typing import Any

from textual.message import Message
from textual.widgets import Static, ListView, ListItem, Label
from textual.containers import Vertical

# from ui.widgets.modais._helpers import _id_safe


class EnvironmentAnalysis(Vertical):
    class Selected(Message):
        def __init__(self, kind: str, ref: Any) -> None:
            super().__init__()
            self.kind = kind  # "item" | "npc"
            self.ref = ref

    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        self._data: dict = {"items": [], "npcs": [], "kind": "?"}

    def compose(self):
        yield Static("[b]🔍 Ambiente[/]", id="analysis_panel_title")
        yield Static("[dim]carregando...[/]", id="analysis_panel_description")
        yield ListView(id="analysis_panel_list")

    def update_analysis_panel(self, details: dict) -> None:
        self._data = details or {}

        title=self.query_one("#analysis_panel_title", Static)
        description=self.query_one("#analysis_panel_description", Static)
        panel_list=self.query_one("#analysis_panel_list", ListView)

        kind = self._data.get("kind", "?")
        attention = self._data.get("attention_used", "?")
        title.update(f"[b]🔍 Ambiente[/] [dim]({kind}, atenção {attention})[/]")
        description.update(f"[dim]{self._data.get('description', '')}[/]")

        new_items: list[ListItem] = []
        # for it in self._data.get("itens", []):
        #     new_items.append(
        #         ListItem(
        #             Label(f"📦 {it}"),
        #             id=f"ai_{_id_safe(str(it))}"
        #         )
        #     )
        for npc in self._data.get("npcs", []):
            new_items.append(
                ListItem(
                    Label(f"👤 [b]{npc['nome']}[/]"),
                    id=f"an_{npc['id']}"
                )
            )
        if not new_items:
            new_items.append(ListItem(Label("[dim](nada de notável aqui)[/]")))

        async def _repopulate():
            await panel_list.clear()
            for li in new_items:
                await panel_list.append(li)

        try:
            self.run_worker(_repopulate(), exclusive=True)
        except Exception:
            pass

    # def on_list_view_selected(self, event: ListView.Selected) -> None:
    #     nid = event.item.id or ""
    #     if nid.startswith("an_"):
    #         self.post_message(self.Selecionado("npc", nid[3:]))
    #     elif nid.startswith("ai_"):
    #         sel_id = nid[3:]
    #         for it in self._data.get("itens", []):
    #             if _id_safe(str(it)) == sel_id:
    #                 self.post_message(self.Selecionado("item", it))
    #                 return