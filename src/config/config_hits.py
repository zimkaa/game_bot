from dotenv import load_dotenv

from buffs.buffs_name import AIR_BARRIER
from buffs.buffs_name import BOUNTY_OF_LIGHTNING
from buffs.buffs_name import FIRE_SHIELD
from buffs.buffs_name import FLAMING_RACK
from buffs.buffs_name import HEADWIND
from buffs.buffs_name import IFRITS_CURSE
from buffs.buffs_name import INCREDIBLE_ACCURACY
from buffs.buffs_name import METEOR_SHIELD
from buffs.buffs_name import POISONING
from buffs.buffs_name import POWER
from buffs.buffs_name import PUSH
from buffs.buffs_name import QUICKSAND
from buffs.buffs_name import SAND_WALL
from buffs.buffs_name import SOURCE
from buffs.buffs_name import STONE_FLESH
from buffs.buffs_name import VULNERABLE_TO_FIRE

from config.variable_names import WARRIOR

from .local_config import PERSON_TYPE

from .variable_names import WARRIOR


load_dotenv()


HIT_SCROLLS = [
    "Свиток Воскрешения",
    "Свиток Выжигания Маны",
    "Свиток Светлого Удара",
    "Свиток Темного Удара",
    "Свиток Изгнания Из Боя",
    "Свиток Удар Ярости",
    "Свиток Излечения Союзника",
    "Свиток Завершения Боя",
    "Свиток Женской Злости",
    "Снежок",
]

if PERSON_TYPE == WARRIOR:
    KICK = [PUSH, INCREDIBLE_ACCURACY]
    BUFFS = [PUSH, INCREDIBLE_ACCURACY]
else:
    BUFFS = [
        BOUNTY_OF_LIGHTNING,
        SAND_WALL,
        POISONING,
        STONE_FLESH,
        POWER,
        METEOR_SHIELD,
        QUICKSAND,
        SOURCE,
    ]
    KICK = [
        VULNERABLE_TO_FIRE,
        FLAMING_RACK,
        IFRITS_CURSE,
        VULNERABLE_TO_FIRE,
        FIRE_SHIELD,
        HEADWIND,
        AIR_BARRIER,
        BOUNTY_OF_LIGHTNING,
        SAND_WALL,
        POISONING,
        STONE_FLESH,
        POWER,
        METEOR_SHIELD,
        QUICKSAND,
        SOURCE,
    ]


HIT_PRIORITY = True

ONLY_NUM_HIT = True
NUMBER_HIT = 0

EVERY_NUM_HIT = True
EVERY_NUMBER_HIT = 5

USE_PROF_HIT_NAME = "Цепная молния"

ANY_PROF_HITS = {
    "name": [
        "Гнев Титанов",
        "Ураган",
        "Молния",
        "Цепная молния",
        "Каменная стрела",
        "Песочная стрела",
        "Колючки",
        "Огненная стрела",
        "Стрела из магмы",
        "Воспламенение",  # old name "Тело-огонь"
    ],
    "code": [207, 208, 205, 206, 123, 122, 94, 37, 124, 56],
    "mp_cost": [75, 100, 50, 150, 75, 50, 75, 50, 75, 75],
    "od": [100, 100, 100, 125, 100, 100, 100, 100, 100, 100],
    "priority": [1, 5, 8, 99, 6, 9, 3, 4, 2, 7],
}

ALL_ANY_PROF_HITS = {
    "name": [
        "Огненная стрела",
        "Воспламенение",  # old name "Тело-огонь"
        "Огненный дождь",
        "Каменный дождь",
        "Колючки",
        "Песочная стрела",
        "Каменная стрела",
        "Стрела из магмы",
        "Ледяная стрела",
        "Ледяная глыба",
        "Прикосновение льдом",
        "Метель",
        "Молния",
        "Цепная молния",
        "Гнев Титанов",
        "Ураган",
        "Смазанный удар",
    ],
    "code": [
        37,
        56,
        81,
        86,
        94,
        122,
        123,
        124,
        144,
        146,
        148,
        184,
        205,
        206,
        207,
        208,
        269,
    ],
    "mp_cost": [
        50,
        75,
        150,
        150,
        75,
        50,
        75,
        75,
        50,
        75,
        75,
        150,
        50,
        150,
        75,
        100,
        0,
    ],
    "od": [
        100,
        100,
        125,
        125,
        100,
        100,
        100,
        100,
        100,
        100,
        100,
        125,
        100,
        125,
        100,
        100,
        90,
    ],
    "priority": [
        1,
        1,
        2,
        2,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        2,
        3,
        99,
        1,
        2,
        99,
    ],
}
