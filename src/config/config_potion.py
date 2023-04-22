from dotenv import load_dotenv

from .potions_name import POTION_OF_BERSERKER_RAGE
from .potions_name import POTION_OF_ELEMENTALIST
from .potions_name import THIRST_FOR_LIFE


load_dotenv()

POTION = "Превосходное Зелье Недосягаемости"

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

COUNT_POTION = 5

NEED_POTIONS = {POTION: COUNT_POTION}
