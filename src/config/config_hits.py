from dotenv import load_dotenv

from buffs import AIR_BARRIER  # noqa: I100
from buffs import BOUNTY_OF_LIGHTNING
from buffs import FIRE_SHIELD
from buffs import FLAMING_RACK
from buffs import HEADWIND
from buffs import IFRITS_CURSE
from buffs import INCREDIBLE_ACCURACY
from buffs import METEOR_SHIELD
from buffs import POISONING
from buffs import POWER
from buffs import PUSH
from buffs import QUICKSAND
from buffs import SAND_WALL
from buffs import SOURCE
from buffs import STONE_FLESH
from buffs import VULNERABLE_TO_FIRE


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


KICK_WARRIOR = [
    PUSH,
    INCREDIBLE_ACCURACY,
]

KICK_MAG = [
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
