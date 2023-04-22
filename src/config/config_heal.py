from dotenv import load_dotenv


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
