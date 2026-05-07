from random import randint as ri
from dataclasses import dataclass

SCALE = 1000

@dataclass
class Modifier:
    value: float
    increases: bool

def probabilidade(percentage: int, fatigue: bool, d20: int = 10, **kwargs: Modifier) -> bool:
    random_num = ri(1, SCALE)
    dice_factor = (d20 - 10) * (SCALE // 100)
    percentage = percentage * (SCALE // 100) + dice_factor
    for mod in kwargs.values():
        if mod.increases:
            if not fatigue:
                percentage += int(mod.value * (SCALE // 100))
        else:
            percentage -= int(mod.value * (SCALE // 100))
    if fatigue:
        percentage -= 30 * (SCALE // 100)
    return percentage >= random_num
        