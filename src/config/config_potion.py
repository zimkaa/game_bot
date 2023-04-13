import os

from dotenv import load_dotenv

from .potions_name import POTION_OF_BERSERKER_RAGE
from .potions_name import POTION_OF_ELEMENTALIST
from .potions_name import THIRST_FOR_LIFE


load_dotenv()

POTION = "Превосходное Зелье Недосягаемости"

# POTION = "Зелье Соколиный Взор"

# POTION = "Превосходное Зелье Панциря"
# POTION = "Превосходное Зелье Человек-Гора"

# 325 - "Жажда Жизни"
# 328 - "Зелье Ярость Берсерка"
# 330 - "Зелье Элементалиста"   старое "Зелье Мифриловый Стержень"
# 33 - "Восстановление MP"  5000

POTION_USE_LIST = [330]  # "Зелье Элементалиста"

DICT_NAME_USE_POTIONS = {
    "name": [
        POTION_OF_ELEMENTALIST,
        POTION_OF_BERSERKER_RAGE,
        THIRST_FOR_LIFE,
    ],
    "code": [330, 328, 325],
    "priority": [0, 0, 1],
    "mp_boost": [0, 0, 0],
    "od": [30, 30, 30],
}


def get_effect_use_pattern(potion: str = POTION) -> str:
    part1 = os.getenv("PART1")
    part2 = f"{potion}"
    part3 = os.getenv("PART3")
    return part1 + part2 + part3
    # return os.getenv('PART4')


COUNT_POTION = 5

NEED_POTIONS = {POTION: COUNT_POTION}
