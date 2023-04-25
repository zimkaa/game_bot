import json
import os
import re
from pathlib import Path
from typing import Any

from config import ANY_PROF_HITS  # noqa: I100
from config import DICT_NAME_BOOST_MP
from config import FIND_FIGHT_VARIABLES_PART1
from config import FIND_FIGHT_VARIABLES_PART2
from config import FIND_LIVES_G2
from config import HIT_SCROLLS
from config import KICK_MAG
from config import KICK_WARRIOR
from config import MAG
from config import MP_LIST_MP
from config import PERSON_TYPE
from config import WARRIOR

from loguru import logger

from pandas import DataFrame
from pandas import concat

from request import send_telegram

from schemas import FightConfig
from schemas import Hit

from .config_fight import get_fight_config


logger.add(
    "battle.log",
    format="{time} {level} {message}",
    filter="fight",
    level="TRACE",
    rotation="10 MB",
    compression="zip",
)


class Fight:
    def __init__(self, nickname: str) -> None:
        self._read_json()
        self._stop = False
        self._scroll = True
        self._hits_df: DataFrame = DataFrame()
        self._dict_hit: dict[str, dict[str, str]]
        self._fight_pm: list[str]
        self._fight_ty: list[str]
        self._param_en: list[str]
        self._param_ow: list[str]
        self._lives_g1: list[str]
        self._lives_g2: list[str]
        self._magic_in: list[str]
        self._alchemy: list[str]
        self._nickname = nickname
        self._bot_count: int

    def setup_value(self, page_text: str) -> None:
        """Fills in the values"""
        self._page_text = page_text
        self._list_hits: list[int] = []

        self._ina = ""
        self._inb = ""
        self._inu = ""

        self._prepare_data()

        if self._param_en:
            self._get_self_info()
            self._get_enemy_info()
            self._print_log()
        else:
            text = f"{self._nickname} wait hit from enemy"
            logger.error(text)
            send_telegram(text)

    def _prepare_data(self) -> None:
        """Creating self attributes"""
        name_list = (
            "_fight_ty",
            "_param_ow",
            "_lives_g1",
            "_lives_g2",
            "_alchemy",
            "_magic_in",
            "_param_en",
            "_fight_pm",
            "_logs",
        )
        for attribute_name in name_list:
            data = self._find_value(attribute_name)
            if data:
                setattr(self, attribute_name, data)

    def _find_value(self, value: str) -> list[str] | list[Any]:
        """Finder"""
        find_value = value[1:]
        if find_value == "lives_g2":
            pattern = FIND_LIVES_G2
        else:
            pattern = FIND_FIGHT_VARIABLES_PART1 + find_value + FIND_FIGHT_VARIABLES_PART2
        page_text = self._page_text
        result: list[str] = re.findall(pattern, page_text)
        if result:
            if find_value == "logs":
                new_res = result[0].replace(",,", ',"was empty in log",')
                new_res2 = f"[{new_res}]"
                return eval(new_res2)
            result_value: list[str] = result[0].replace("]", "").replace('"', "").replace("[", "").split(",")
            return result_value

        if find_value == "alchemy":
            logger.debug("alchemy empty Потому что только часть атрибутов доступна")
            return []

        logger.debug(f"{type(self._page_text)}")
        logger.debug(f"{find_value=} {result=}")
        text = f"{self._nickname} Trouble {find_value=} {result=}"
        logger.error(text)
        send_telegram(text)
        raise

    def _get_self_info(self) -> None:
        """Create info about person"""
        if self._param_ow:
            self._my_mp = float(self._param_ow[3])
            self._my_all_mp = float(self._param_ow[4])
            self._my_hp = float(self._param_ow[1])
            self._my_all_hp = float(self._param_ow[2])
        if self._fight_pm:
            self._simple_hit_od = int(self._fight_pm[2])
            self._my_od = int(self._fight_pm[1])

    def _get_enemy_info(self) -> None:
        """Create info about enemy"""
        self._bot_name = self._param_en[0]
        self._bot_hp = float(self._param_en[1])
        self._bot_max_hp = float(self._param_en[2])
        self._bot_mp = float(self._param_en[3])
        self._bot_max_mp = float(self._param_en[4])
        self._bot_level = self._param_en[5]

    def _print_log(self) -> None:
        """Create log message"""
        first = f"bot_level={self._bot_level} bot_hp={self._bot_hp}"
        second = f" my_od={self._my_od} my_mp={self._my_mp}"
        third = f" my_hp={self._my_hp}"
        text = first + second + third
        logger.info(text)
        logger.trace(f"{self._magic_in=}")

    def get_state(self) -> tuple[int, float, float]:
        """Get my_od, my_mp, my_hp

        :return: (my_od, my_mp, my_hp)
        :rtype: tuple[int, float, float]
        """
        return self._my_od, self._my_mp, self._my_hp

    def _heal_check(self, value: float, need_to_check: float) -> bool:
        """Checking heals

        :param value: _description_
        :type value: _type_
        :param need_to_check: _description_
        :type need_to_check: _type_
        :return: _description_
        :rtype: bool
        """
        if value <= need_to_check:
            return True
        return False

    def _check_potion(self, my_list: list[int]) -> list[int]:
        """Check if exist potion

        :param my_list: list of potion
        :type my_list: list[int]
        """
        magic = list()
        for value in self._magic_in:
            int_value = int(value)
            if int_value in my_list:
                magic.append(int_value)
        if not magic:
            text = f"{self._nickname} No item on belt in fight or scroll"
            logger.critical(text)
        return magic

    def _create_sorted_df(self, df: DataFrame, magic: list[int]) -> DataFrame:
        """Create new sorted DF (DataFrame)"""
        query = list()
        list_element = list()
        for num, element in enumerate(magic):
            for index_num in df.index:
                if df["code"][index_num] == element:
                    query.append(f"{element}_{self._alchemy[num]}@")
                    list_element.append(element)
        new_df = DataFrame()
        for name in list_element:
            result = df[df["code"] == name]
            new_df = concat([new_df, result], ignore_index=True)
        new_df["query"] = query
        sorted_list_df = new_df.sort_values(by="priority")
        return sorted_list_df

    def _using_mp(self) -> None:
        """Add restore MP to request"""
        logger.info("---------------Use MP--------------------")
        boost_mp = 0
        for index_num in self._sorted_df.index:
            boost_mp += int(self._sorted_df["mp_boost"][index_num])
            query_mp = self._sorted_df["query"][index_num]
            condition = boost_mp - self._fight_config.MP_NEED_INSIDE_BATTLE
            if self._my_od <= 30:
                break
            self._my_od -= int(self._sorted_df["od"][index_num])
            if condition >= 0:
                self._ina += query_mp
                break
            else:
                self._ina += query_mp
        part1 = f"{self._nickname} USING MP ina={self._ina} my_mp={self._my_mp}"
        part2 = f" MP_NEED_INSIDE_BATTLE={self._fight_config.MP_NEED_INSIDE_BATTLE}"
        part3 = f" condition {condition} boost_mp={boost_mp}"
        part4 = f" my_od={self._my_od}"
        text = part1 + part2 + part3 + part4
        logger.critical(text)

    def _heal_mp(self) -> None:
        """Checking if can add to the request"""
        magic = self._check_potion(MP_LIST_MP)
        if magic:
            df = DataFrame(DICT_NAME_BOOST_MP)
            self._sorted_df = self._create_sorted_df(df, magic)
            self._using_mp()

    def _using(self, sorted_df: DataFrame) -> None:
        """Add using potion to request"""
        logger.info("---------------Use--------------------")
        if self._my_od >= 110:
            for index_num in sorted_df.index:
                query_mp = sorted_df["query"][index_num]
                self._ina += query_mp
                self._my_od -= int(sorted_df["od"][index_num])

        part1 = f"{self._nickname} USING ina={self._ina}"
        part4 = f" my_od={self._my_od}"
        text = part1 + part4
        logger.critical(text)

    def _heal_hp(self) -> None:
        """ONLY MAG HEAL!!!! Add heal to request"""
        self._ina += "320@"
        self._my_od -= 30
        text = f"{self._nickname} _heal_hp {self._my_hp=} {self._my_all_hp=}"
        logger.debug(text)

    def _read_json(self) -> None:
        """Create all dict_hits"""
        dir_path = Path(__file__).parent.resolve()
        file_name = "hit_dict"
        file_path = os.path.join(dir_path, "settings", f"{file_name}.json")

        with open(file_path, "r", encoding="utf8") as file:
            self._dict_hit = json.loads(file.read())

    def _check_use_hp(self) -> None:
        """Check and use HP"""
        if self._fight_config.HP:
            need_hp = self._conditions_heal(self._my_all_hp, needed_percent=self._fight_config.NEED_HP_PERCENT)
            logger.warning(f"{need_hp=}")
            if self._heal_check(self._my_hp, need_hp):
                self._heal_hp()

    def _check_use_mp(self) -> None:
        """Check and use MP"""
        if self._fight_config.MP:
            logger.warning(f"{self._my_all_mp=}")

            need_mp = self._conditions_heal(self._my_all_mp, need=self._fight_config.NEED_MP_COUNT)
            logger.warning(f"{need_mp=}")
            if self._heal_check(self._my_mp, need_mp):
                logger.error(f"\n{need_mp=} {self._my_mp=}\n")
                self._heal_mp()

    def _check_use_stable_mag_hit(self) -> None:
        """Check need use or not
        Check MP and use or not stable mag hit
        """
        min_mp_coefficient = self._fight_config.MIN_MP_COEFFICIENT
        min_mp_for_hits = self._my_all_mp * min_mp_coefficient

        self._hit = DataFrame()

        if self._my_mp > min_mp_for_hits:
            if self._fight_config.STABLE_MAGIC_HIT:
                stable_magic_hit = self._prepares_stable_magic_hit()
                self._hit = DataFrame(stable_magic_hit).sort_values(by="priority")
        else:
            text = f"{self._nickname} Not enough MP for mag hit {self._my_mp} < {min_mp_for_hits}"
            logger.warning(text)

    def _check_use_stable_hit(self) -> None:
        """Check need use or not stable hit"""
        if self._fight_config.STABLE_HIT:
            stable_hit = self._prepares_stable_hit()
            if self._hit.empty:
                self._hit = DataFrame(stable_hit).sort_values(by="priority")

    def _check_use_kick(self) -> None:
        """Check use or not kick and use"""
        if self._fight_config.KICK:
            if PERSON_TYPE == WARRIOR:
                self._use_kick(KICK_WARRIOR)
            else:
                self._use_kick(KICK_MAG)

    def _check_use_scroll(self) -> None:
        """Check use or not scroll and use"""
        if self._fight_config.SCROLL:
            if self._scroll:
                self._use_scroll(HIT_SCROLLS[5])

    def _init_fight_config(self) -> None:
        """Initializing fight_config"""
        config = None
        bot_group = None

        file_name = f"fight_config_{PERSON_TYPE}"
        logger.critical(f"{file_name=}")
        fight_conf = get_fight_config(file_name)
        for element in fight_conf:
            if self._bot_name in element["names"]:
                bot_group = element
                for key, value in element["level_group"].items():
                    if self._bot_level in value:
                        config = element["level"].get(key)
                        break
                break

        if not config:
            if bot_group:
                config = bot_group["level"].get("default")
                logger.warning(f"Set default {config=}")

        if config:
            self._fight_config = FightConfig(**config)
        else:
            text = f"{self._nickname} Fight config not found. {self._bot_name=} Use default!!!"
            logger.critical(text)
            send_telegram(text)
            self._fight_config = FightConfig()

    def _init_config(self) -> None:
        """int config"""
        self._init_fight_config()

        self._check_use_hp()

        self._check_use_mp()

        logger.trace(f"{self._magic_in=}")

        self._check_use_stable_mag_hit()

        self._check_use_stable_hit()

        self._check_use_scroll()

    def _prepares_stable_hit(self) -> dict:
        """Create stable_hit dict to DF"""
        hit_od = self._simple_hit_od
        stable_hits = {
            "name": [
                "Прицельный",
                "Простой",
            ],
            "code": [1, 0],
            "mp_cost": [0, 0],
            "od": [hit_od + 20, hit_od],
            "priority": [0, 1],
        }
        return stable_hits

    def _prepares_stable_magic_hit(self) -> dict:
        """Create stable_magic_hit dict to DF"""
        mp_hit = self._fight_config.MP_HIT
        stable_magic_hit = {
            "name": [
                "Mind Blast",
                "Spirit Arrow",
            ],
            "code": [3, 2],
            "mp_cost": [mp_hit, mp_hit],
            "od": [90, 50],
            "priority": [0, 1],
        }
        return stable_magic_hit

    def fight(self) -> None:
        """Start fight"""
        self._all_info()

        self._init_config()

        self._get_hit()

        self._check_use_kick()

        self._get_query()

    def _all_info(self) -> None:
        """Get info on console log"""
        number = 2
        hp_bots = []
        len_lives_g1 = len(self._lives_g1)
        if len_lives_g1 % 5 == 0:
            value = self._lives_g1
            max_number_iter = int(len_lives_g1 / 5)
        else:
            max_number_iter = int(len(self._lives_g2) / 5)
            value = self._lives_g2
        for _ in range(max_number_iter):
            hp_bots.append(value[number])
            number += 5
        text = f"hp_bots = {hp_bots}"
        self._bot_count = len(hp_bots)
        logger.info(text)
        text2 = f"bot_name = {self._bot_name}"
        logger.success(text2)

    def _conditions_heal(self, maximum: float, needed_percent: float = 0.0, need: float = 0.0) -> float:
        """Get value for minimum hp or mp

        :param maximum: maximum value
        :type maximum: float
        :param needed_percent: needed percent value, defaults to None
        :type needed_percent: float, optional
        :param need: needed value, defaults to None
        :type need: float, optional
        :return: needed value
        :rtype: float
        """
        if needed_percent and need:
            min_value = maximum * needed_percent
            if min_value > need:
                return min_value
            return need
        elif needed_percent:
            return maximum * needed_percent
        return need

    def _use_scroll(self, scroll: str) -> None:
        """Add scroll to request"""
        self._convert_name_to_value(scroll)
        if self._my_od >= (30 + self._item_od):
            for num, element in enumerate(self._magic_in):
                if self._item_value == element:
                    self._ina += f"{self._item_value}_{self._alchemy[num]}@"
                    self._my_od -= self._item_od

    def _convert_name_to_value(self, name: str) -> None:
        """Create new attributes"""
        self._item_value = str(self._dict_hit[name]["number"])
        self._item_od = int(self._dict_hit[name]["od"])
        self._item_mp = int(self._dict_hit[name]["mp"])

    def _use_kick(self, kicks: list[str]) -> None:
        """Add powered hit this is use mag buff
        or it can be used of warrior top hit"""
        count = self._fight_config.KICK_COUNT
        for item in kicks:
            if count:
                self._convert_name_to_value(item)
                if self._my_od >= self._item_od:
                    if self._item_value in self._magic_in:
                        if f"{self._item_value}@" not in self._ina:
                            self._ina += f"{self._item_value}@"
                            self._my_od -= self._item_od
                            count -= 1
                            text = f"using KICK {self._item_value=}"
                            logger.debug(text)

    def _get_hit(self) -> None:
        """Create hit for the current turn"""
        if PERSON_TYPE == MAG and self._my_mp > 300:
            self._check_in_prof_hits()
            self._preparation_big_hit()
        elif PERSON_TYPE == WARRIOR:
            self._check_in_prof_hits()
            self._preparation_big_hit()

        self._preparation_small_hit()

        self._aggregate_df_hits()

    def _check_in_prof_hits(self) -> None:
        """Check super hit and create sorted DF"""
        self._hits_df = DataFrame()
        if self._fight_config.SUPER_HIT:
            all_hits_df = DataFrame(ANY_PROF_HITS)
            for element in self._magic_in:
                self._hits_df = concat(
                    [self._hits_df, all_hits_df[all_hits_df["code"] == int(element)]],
                    ignore_index=True,
                )

        if self._hits_df.empty:
            logger.info("cooldown magic hit skills")
            self._check_use_kick()
        else:
            self._hits_df = self._hits_df.sort_values(by="priority")

    def _preparation_big_hit(self) -> None:
        """Prepare big hit"""
        first_hit_boost_od = 0
        second_hit_boost_od = 25
        third_hit_boost_od = 50
        od_dict = {0: first_hit_boost_od, 1: second_hit_boost_od, 2: third_hit_boost_od}
        num_iteration = 3

        if not self._hits_df.empty:
            for iteration in range(num_iteration):
                for num in self._hits_df["od"].index:
                    if self._hits_df["name"][num] == "Цепная молния":
                        continue

                    od = od_dict.get(iteration) + self._hits_df["od"][num]
                    if self._my_od >= int(od):
                        element = self._hits_df["code"][num]
                        self._my_od -= od
                        self._list_hits.append(element)
                        break

    def _preparation_small_hit(self) -> None:
        """Prepare small hit"""
        first_hit_boost_od = 0
        second_hit_boost_od = 25
        third_hit_boost_od = 50
        if self._list_hits:
            have_count = len(self._list_hits)
            if have_count == 1:
                od_dict = {0: second_hit_boost_od, 1: third_hit_boost_od}
            elif have_count == 2:
                od_dict = {0: third_hit_boost_od}
        else:
            od_dict = {0: first_hit_boost_od, 1: second_hit_boost_od, 2: third_hit_boost_od}
            have_count = 0

        new_count = 3 - have_count
        if new_count != 0:
            self._od_hit_check(new_count, od_dict)

    def _od_hit_check(self, count: int, od_dict: dict) -> None:
        """Check od per hit and add it if ok"""
        for iteration in range(count):
            if not self._hit.empty:
                for num in self._hit["od"].index:
                    od = od_dict.get(iteration) + self._hit["od"][num]
                    if self._my_od >= int(od):
                        element = self._hit["code"][num]
                        self._my_od -= od
                        self._list_hits.append(element)
                        break

    def _aggregate_df_hits(self) -> None:
        """Aggregate DF hits"""
        self._aggregate_hits = concat([self._hits_df, self._hit], ignore_index=True)

    def _get_query(self) -> None:
        """
        Create query part 'inu'
        """
        for num, value in enumerate(self._list_hits):
            mp = self._aggregate_hits[self._aggregate_hits["code"] == value].iloc[0]["mp_cost"]
            self._inu += f"{num}_{value}_{mp}@"

    def get_queries_param(self) -> Hit:
        """Get query hit prams"""
        data = {"inu": self._inu, "inb": self._inb, "ina": self._ina}
        return Hit(**data)

    def get_data(self) -> dict[str, str]:
        """Get query data
        It can return dict with retry
        """
        if self._stop:
            return {"retry": "True"}
        data = {
            "post_id": "7",
            "vcode": self._fight_pm[4],
            "enemy": self._fight_pm[5],
            "group": self._fight_pm[6],
            "inf_bot": self._fight_pm[7],
            "inf_zb": self._fight_pm[10],
            "lev_bot": self._param_en[5],
            "ftr": self._fight_ty[2],
            "inu": self._inu,
            "inb": self._inb,
            "ina": self._ina,
        }
        return data
