from enum import Enum

from .elixir import Elixir


class Summon(str, Enum):
    PLANAR = Elixir.PLANAR_SUMMONING.value
    BAIT = Elixir.BOT_BAIT.value


class SummonBotType:
    _state = True

    def __init__(self, *, first_item: Summon, second_item: Summon) -> None:
        self._item = first_item
        self._inverse_item = second_item

    @property
    def name(self) -> str:
        if self._state:
            return self._item.value
        return self._inverse_item.value

    def change_bot(self) -> None:
        self._state = not self._state
