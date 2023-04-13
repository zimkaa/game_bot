from dotenv import load_dotenv

from heal.healing_potion_name import ENERGY_POTION
from heal.healing_potion_name import EXCELLENT_MANA_POTION


load_dotenv()


MP_LIST_MP = [337, 521, 33, 306, 309]

DICT_NAME_BOOST_MP = {
    "name": [
        "Тыквенное зелье",
        "Превосходное Зелье Маны",
        "Восстановление MP",  # it's can be 500 MP or 5000 MP or anything else
        "Зелье Восстановления Маны",
        "Зелье Энергии",
    ],
    "code": MP_LIST_MP,
    "priority": [0, 1, 2, 3, 4],
    "mp_boost": [999, 500, 5_000, 100, 100],
    "od": [30, 30, 30, 30, 30],
}

DUNGEON_MP_HEALING_BEFORE_BOT = 0.15  # 0.15

DUNGEON_MP_HEALING_BEFORE_BOSS = 0.2

DUNGEON_HP_HEALING_BEFORE_BOT = 0.2

DUNGEON_HP_HEALING_BEFORE_BOSS = 0.99

DUNGEON_MP_NEED_BEFORE_BOSS_FOR_MAG = 2_000

DUNGEON_MP_NEED_BEFORE_BOSS_FOR_WARRIOR = 0

DUNGEON_HP_HEALING_BEFORE_BOSS_POTION_HP = ENERGY_POTION

DUNGEON_HP_HEALING_BEFORE_BOSS_POTION_MP = EXCELLENT_MANA_POTION
