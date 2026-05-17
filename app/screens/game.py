from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button

from core.world.world import World
from core.world.region import Region

from core.time.manager import TimeManager
from core.systems import register_systems
from core.events import event_bus, WorldLogMessage

from core.entity import Entity
from core.entity.components import (
    LocationComponent, WorldKnowledgeComponent
)

from app.screens.base import BaseScreen

from app.widgets.status import PainelStatus
from app.widgets.world_log import WorldLog
from app.widgets.map import MiniMap
from app.widgets.analyze import EnvironmentAnalysis

from app.screens.mixins._movement import MovementMixin


class GameRunning(
    BaseScreen, MovementMixin):
    
    BINDINGS = [
        ("S", "save",  "Salvar"),
        ("H", "back_to_menu", "Menu"),
        ("left", "move_left"),
        ("right", "move_right"),
        ("up", "move_up"),
        ("down", "move_down")
    ]

    def __init__(self, world: World) -> None:
        super().__init__()
        self.direction:str=""

        self.world = world

        player = world.main_player()
        assert player is not None
        self.player: Entity = player

        self.world_knowledge = self.player.require(WorldKnowledgeComponent)
        self.loc = self.player.require(LocationComponent)

        region = world.get_region(
            self.loc.region_name
        )
        assert region is not None
        self.world_region:Region=region

        self.time_manager = TimeManager(world, step_minutes=1)
        self._time_auto_timer=None
        self._time_play_timer=None
        
        event_bus.clear()
        register_systems(self.world)

    def compose_body(self) -> ComposeResult:
        map = MiniMap(self.world_region, self.loc, self.world_knowledge, id="map")
        status = PainelStatus(self.player, id="status")

        time_bar = Horizontal(
            Button("▶ Auto",        id="btn_time_play",    variant="success"),
            Button("⏸ Pausar",      id="btn_time_stop",    variant="warning"),
            Button("⏩ Avançar...",  id="btn_time_forward", variant="primary"),
            Button("⏭ +1 hora",     id="btn_time_60",      variant="default"),
            id="time_bar",
        )

        log = WorldLog(id="world_log")
        log.add_event(f"[b cyan]Bem-vindo, {self.player.name}.[/]")

        environment = EnvironmentAnalysis(id="analysis_panel")

        yield Vertical(
            Horizontal(
                map,
                Vertical(
                    status,
                    time_bar,
                    id="status_col"
                ),
                id="top"
            ),
            Horizontal(
                environment,
                log,
                id="middle"
            ),
            id="game_root",
        )

    def on_mount(self) -> None:
        self._map = self.query_one("#map", MiniMap)
        self._status = self.query_one("#status", PainelStatus)
        self._log = self.query_one("#world_log", WorldLog)
        self._analysis_panel = self.query_one("#analysis_panel", EnvironmentAnalysis)

        event_bus.subscribe_fn(WorldLogMessage, self._on_log_msg)
        self._update_status
        self._analysis_panel.update_analysis_panel()

    @property
    def _update_status(self) -> None:
        self._status.update_status(self.player, time_str=self.time_manager.now())

    def _on_log_msg(self, ev: WorldLogMessage) -> None:
        self._log.add_event(ev.text)

    def on_button_pressed(self,event:Button.Pressed)->None:
        self.notify(str(event.button.id), timeout=1)

    def action_save(self) -> None:
        from data import save_game
        try:
            ts = save_game(self.world)
            self.notify(f"Jogo salvo ({ts}).")
        except Exception as e:
            self.notify(f"Erro ao salvar: {e}", severity="error")

    def action_back_to_menu(self) -> None:
        from app.screens.menu import MainMenu
        self.app.push_screen(MainMenu())

    def action_move_left(self)->None:
        self._move("left") # type: ignore

    def action_move_right(self)->None:
        self._move("right") 

    def action_move_up(self)->None:
        self._move("up") 

    def action_move_down(self)->None:
        self._move("down")
