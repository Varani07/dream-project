import uuid
from dataclasses import dataclass
from typing import TypeVar, Type, cast, Self


@dataclass
class Component: pass

T = TypeVar("T", bound=Component)

class Entity:
    def __init__(self, nome: str, entity_id: str|None = None) -> None:
        self.id = entity_id or str(uuid.uuid4())
        self.nome = nome
        self._components: dict[type, Component] = {}

    def add(self, comp: Component) -> Self:
        self._components[type(comp)] = comp
        return self
    
    def get(self, comp_type: Type[T]) -> T | None:
        result = self._components.get(comp_type)
        return cast(T | None, result)
    
    def has(self, comp_type: Type[Component]) -> bool:
        return comp_type in self._components
    
    def all_components(self) -> dict[str, Component]:
        return {type(c).__name__: c for c in self._components.values()}
    