import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Type, TypeVar
import logging
log = logging.getLogger("event_bus")

@dataclass
class Event: pass

T = TypeVar("T", bound=Event)
type Handler[T] = Callable[[T], None]

class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[Type[Event], list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: Type[T]) -> Callable[[Handler[T]], Handler[T]]:
        def decorator(fn: Handler[T]) -> Handler[T]:
            self._subscribers[event_type].append(fn)
            return fn
        return decorator
    
    def subscribe_fn(self, event_type: Type[T], fn: Handler[T]) -> None:
        self._subscribers[event_type].append(fn)
    
    def publish(self, event: Event) -> None:
        for fn in list(self._subscribers[type(event)]):
            try: fn(event)
            except Exception as e:
                log.exception("Subscriber %s falhou em %s: %s", fn, event, e)

    def clear(self) -> None: self._subscribers.clear()

event_bus = EventBus()