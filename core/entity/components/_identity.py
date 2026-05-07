from dataclasses import dataclass
from core.entity.entity import Component

@dataclass
class IdentityComponent(Component):
    social_class: str = "comum"
    public_name: str = ""

@dataclass
class PlayerControlComponent(Component):
    pass
