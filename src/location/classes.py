from enum import Enum


class Location(str, Enum):
    CITY = "CITY"
    FIGHT = "FIGHT"
    INVENTORY = "INVENTORY"
    NATURE = "NATURE"
    ELIXIR = "ELIXIR"
    INFO = "INFO"
