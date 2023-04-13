from dataclasses import dataclass

from .bot_names import ARCHI_LICH
from .bot_names import ARCHI_PALADIN_MORTIUS
from .bot_names import FOREST_KEEPER
from .bot_names import GROMLECH_BANDIT
from .bot_names import GROMLECH_BLUETOOTH
from .bot_names import GROMLECH_WIZARD
from .bot_names import HELPER_OF_ATAMAN
from .bot_names import KHALGHAN_RAIDER
from .bot_names import LICH
from .bot_names import MINION_OF_LOKAR
from .bot_names import PALADIN_MORTIUS
from .bot_names import PLAGUE_ZOMBIE
from .bot_names import RENEGADE_DRUID


FORPOST_BOSSES = [
    MINION_OF_LOKAR,
    HELPER_OF_ATAMAN,
    GROMLECH_BLUETOOTH,
    RENEGADE_DRUID,
    FOREST_KEEPER,
]

FORPOST_BOTS = [
    GROMLECH_WIZARD,
    GROMLECH_BANDIT,
]

OKTAL_BOSSES = [
    KHALGHAN_RAIDER,
]

CITY_BOSSES = FORPOST_BOSSES + OKTAL_BOSSES

DUNGEON_WARRIOR_BOSSES = [
    ARCHI_PALADIN_MORTIUS,
    PALADIN_MORTIUS,
]

DUNGEON_MAG_BOSSES = [
    ARCHI_LICH,
    LICH,
]

DUNGEON_BOTS = [
    PLAGUE_ZOMBIE,
]

DUNGEON_BOSSES = DUNGEON_WARRIOR_BOSSES + DUNGEON_MAG_BOSSES

DUNGEON_BOSSES_AND_BOTS = DUNGEON_BOSSES + DUNGEON_BOTS


@dataclass
class Boss:
    name: str
