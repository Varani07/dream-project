from datetime import timedelta

from core.events import event_bus, TimeAdvanced
from core.world.world import World


class TimeManager:
    def __init__(self, world: World, step_minutes: int = 5) -> None:
        self.world = world
        self.step_min = step_minutes

    def now(self) -> str:
        return self.world.time.strftime("%d/%m/%Y %H:%M")
    
    def _advance(self, minutes: int, reason: str) -> None:
        yesterday = self.world.time.date()
        self.world.time += timedelta(minutes=minutes)
        event_bus.publish(TimeAdvanced(
            minutes=minutes, new_datetime=self.world.time, reason=reason,
            new_day=self.world.time.date() != yesterday,
        ))

    def advance_in_steps(self, minutes: int, reason: str = "action") -> None:
        if minutes <= 0:
            return
        for _ in range(minutes):
            self._advance(1, reason=reason)
