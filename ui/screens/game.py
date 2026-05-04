from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button

from core.world.world import World
from core.time.manager import TimeManager
from core.systems import registrar_sistemas
from core.events import event_bus, LogMundoMensagem
from core.entity import Entity

from ui.screens.base import BaseScreen
from ui.widgets.status import PainelStatus
from ui.widgets.log_mundo import LogMundo


class GameRunning(BaseScreen):
    BINDINGS = [
        ("S", "save",  "Salvar"),
        ("H", "voltar_menu", "Menu"),
    ]

    def __init__(self, world: World) -> None:
        super().__init__()
        self.world = world
        player = world.main_player()
        if player is None:
            raise RuntimeError("World sem player — bug na fábrica?")
        self.player: Entity = player

        self.time_manager = TimeManager(world, step_minutos=5)
        
        event_bus.clear()
        registrar_sistemas(self.world)

    def compose_body(self) -> ComposeResult:
        yield Vertical(
            PainelStatus(self.player, id="status"),
            Static("[dim]Pressione +5 min para o tempo passar.[/]"),
            Horizontal(
                Button("⏩ +5 min", id="btn_avancar5", variant="primary"),
                Button("💾 Salvar (s)", id="btn_save"),
                id="barra_acoes",
            ),
            LogMundo(id="log_mundo"),
            id="game_root",
        )

    def on_mount(self) -> None:
        self._status = self.query_one("#status", PainelStatus)
        self._log = self.query_one("#log_mundo", LogMundo)

        event_bus.subscribe_fn(LogMundoMensagem, self._on_log_msg)

        self._atualizar_status
        self._log.add_evento(f"[b cyan]Bem-vindo, {self.player.nome}.[/]")

    @property
    def _atualizar_status(self) -> None:
        self._status.atualizar(self.player, tempo_str=self.time_manager.now())

    def _on_log_msg(self, ev: LogMundoMensagem) -> None:
        self._log.add_evento(ev.texto)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn_avancar5":
            self.time_manager.avancar_simples(5, motivo="manual")
            self._atualizar_status
        elif bid == "btn_save":
            self.action_save()

    def action_save(self) -> None:
        from data import salvar_jogo
        try:
            ts = salvar_jogo(self.world)
            self.notify(f"Jogo salvo ({ts}).")
        except Exception as e:
            self.notify(f"Erro ao salvar: {e}", severity="error")

    def action_voltar_menu(self) -> None:
        from ui.screens.menu import MenuInicial
        self.app.push_screen(MenuInicial())
