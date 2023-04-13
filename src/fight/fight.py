import json
import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from my_errors import FirstError

from config.config_hits import KICK
from config.config_hits import ANY_PROF_HITS
from config.config_hits import HIT_SCROLLS

from config.config_heal import MP_LIST_MP
from config.config_heal import DICT_NAME_BOOST_MP

from config.config_potion import POTION_USE_LIST
from config.config_potion import DICT_NAME_USE_POTIONS

from config.pattern import FIND_LIVES_G2
from config.pattern import FIND_FIGHT_VARIABLES_PART1
from config.pattern import FIND_FIGHT_VARIABLES_PART2


from config.local_config import PERSON_ROLE
from config.local_config import PERSON_TYPE
from config.local_config import NICKNAME


from bots.bot_names import PLAGUE_ZOMBIE

from buffs.buffs_name import SAND_WALL

from schemas import FightConfig
from schemas import Hit

from request import send_telegram

from config.variable_names import SLAVE
from config.variable_names import MAG
from config.variable_names import WARRIOR

from config.local_config import PERSON_TYPE

from .config_fight import get_fight_config


logger.add(
    "battle.log", format="{time} {level} {message}", filter="fight", level="TRACE", rotation="10 MB", compression="zip"
)


class Fight:
    def __init__(self) -> None:
        self._read_json()
        self.stop = False
        self.scroll = True
        self.hits_df: pd.DataFrame = pd.DataFrame()
        self.dict_hit: dict
        self.magic: list[int] = list()
        self.fight_pm: list[str]
        self.logs: str = ""
        self.fight_ty: list[str]
        self.param_en: list[str]
        self.param_ow: list[str]
        self.lives_g1: list[str]
        self.lives_g2: list[str]
        self.magic_in: list[str]
        self.alchemy: list[str]

    def setup_value(self, page_text: str, fight_iteration: int) -> None:
        """Fills in the values"""
        self.__page_text = page_text
        self.fight_iteration = fight_iteration
        self.list_hits: list[int] = []

        self.ina = ""
        self.inb = ""
        self.inu = ""

        self._prepare_data()

        if self.param_en:
            self._get_self_info()
            self._get_enemy_info()
            self._print_log()
        else:
            text = f"{NICKNAME} wait hit from enemy"
            logger.error(text)
            send_telegram(text)

    def _prepare_data(self) -> None:
        """Creating self attributes"""
        name_list = (
            "fight_ty",
            "param_ow",
            "lives_g1",
            "lives_g2",
            "alchemy",
            "magic_in",
            "param_en",
            "fight_pm",
            "logs",
        )
        for attribute_name in name_list:
            data = self._find_value(attribute_name)
            if data:
                setattr(self, attribute_name, data)

    def _find_value(self, value: str) -> list[str] | list[Any]:
        """Finder"""
        if value == "lives_g2":
            pattern = FIND_LIVES_G2
        else:
            pattern = FIND_FIGHT_VARIABLES_PART1 + value + FIND_FIGHT_VARIABLES_PART2
        result: list[str] = re.findall(pattern, self.__page_text)
        if result:
            if value == "logs":
                new_res = result[0].replace(",,", ',"was empty in log",')
                new_res2 = f"[{new_res}]"
                return eval(new_res2)
            result_value: list[str] = result[0].replace("]", "").replace('"', "").replace("[", "").split(",")
            return result_value

        if value == "alchemy":
            logger.debug("alchemy empty")
            return []

        if value == "fight_ty":
            logger.debug("fight_ty empty")
            return []

        if value == "param_ow":
            logger.debug("param_ow empty")
            return []

        if value == "lives_g1":
            logger.debug("lives_g1 empty")
            return []

        if value == "lives_g2":
            logger.debug("lives_g2 empty")
            return []

        if value == "magic_in":
            logger.debug("magic_in empty")
            return []

        if value == "param_en":
            logger.debug("param_en empty")
            return []

        logger.debug(f"{type(self.__page_text)}")
        logger.debug(f"{result=}")
        text = f"{NICKNAME} Trouble"
        logger.error(text)
        send_telegram(text)
        raise FirstError(text)

    def _get_self_info(self) -> None:
        """Create info about person"""
        if self.param_ow:
            self.my_mp = float(self.param_ow[3])
            self.my_all_mp = float(self.param_ow[4])
            self.my_hp = float(self.param_ow[1])
            self.my_all_hp = float(self.param_ow[2])
        if self.fight_pm:
            self.simple_hit_od = int(self.fight_pm[2])
            self.my_od = int(self.fight_pm[1])

    def _get_enemy_info(self) -> None:
        """Create info about enemy"""
        self.bot_name = self.param_en[0]
        self.bot_hp = int(self.param_en[1])
        self.bot_max_hp = int(self.param_en[2])
        self.bot_mp = int(self.param_en[3])
        self.bot_max_mp = int(self.param_en[4])
        self.bot_level = self.param_en[5]

    def _print_log(self) -> None:
        """Create log message"""
        first = f"bot_level={self.bot_level} bot_hp={self.bot_hp}"
        second = f" my_od={self.my_od} my_mp={self.my_mp}"
        third = f" my_hp={self.my_hp}"
        text = first + second + third
        logger.info(text)
        logger.trace(f"{self.magic_in=}")

    def get_state(self) -> tuple[int, int, int]:
        """Get my_od, my_mp

        :return: (my_od, my_mp)
        :rtype: tuple[int, int]
        """
        return self.my_od, self.my_mp, self.my_hp

    def get_bot_name(self) -> str:
        """Bot name"""
        return self.bot_name

    def __repr__(self) -> str:
        """return only alchemy"""
        text = f"self.alchemy= {self.alchemy}"
        return text

    def _heal_check(self, value: int, need_to_check: float) -> bool:
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
        for value in self.magic_in:
            int_value = int(value)
            if int_value in my_list:
                magic.append(int_value)
        if not magic:
            text = f"{NICKNAME} No item on belt in fight or scroll"
            logger.critical(text)
        return magic

    def _create_sorted_df(self, df: pd.DataFrame, magic: list[int]) -> pd.DataFrame:
        """Create new sorted DF (DataFrame)"""
        query = list()
        list_element = list()
        for num, element in enumerate(magic):
            for index_num in df.index:
                if df["code"][index_num] == element:
                    query.append(f"{element}_{self.alchemy[num]}@")
                    list_element.append(element)
        new_df = pd.DataFrame()
        for name in list_element:
            result = df[df["code"] == name]
            new_df = pd.concat([new_df, result], ignore_index=True)
        new_df["query"] = query
        sorted_list_df = new_df.sort_values(by="priority")
        return sorted_list_df

    def _using_mp(self) -> None:
        """Add restore MP to request"""
        logger.info("---------------Use MP--------------------")
        boost_mp = 0
        for index_num in self.sorted_df.index:
            boost_mp += int(self.sorted_df["mp_boost"][index_num])
            query_mp = self.sorted_df["query"][index_num]
            condition = boost_mp - self.fight_config.MP_NEED_INSIDE_BATTLE
            if self.my_od <= 30:
                break
            self.my_od -= int(self.sorted_df["od"][index_num])
            if condition >= 0:
                self.ina += query_mp
                break
            else:
                self.ina += query_mp
        part1 = f"{NICKNAME} USING MP ina={self.ina} my_mp={self.my_mp}"
        part2 = f" MP_NEED_INSIDE_BATTLE={self.fight_config.MP_NEED_INSIDE_BATTLE}"
        part3 = f" condition {condition} boost_mp={boost_mp}"
        part4 = f" my_od={self.my_od}"
        text = part1 + part2 + part3 + part4
        logger.critical(text)

    def _heal_mp(self) -> None:
        """Checking if can add to the request"""
        magic = self._check_potion(MP_LIST_MP)
        if magic:
            df = pd.DataFrame(DICT_NAME_BOOST_MP)
            self.sorted_df = self._create_sorted_df(df, magic)
            self._using_mp()

    def _using(self, sorted_df) -> None:
        """Add using potion to request"""
        logger.info("---------------Use--------------------")
        if self.my_od >= 110:
            for index_num in sorted_df.index:
                query_mp = sorted_df["query"][index_num]
                self.ina += query_mp
                self.my_od -= int(sorted_df["od"][index_num])

        part1 = f"{NICKNAME} USING ina={self.ina}"
        part4 = f" my_od={self.my_od}"
        text = part1 + part4
        logger.critical(text)

    def strong_potion(self) -> None:
        """Checking if can add to the request potion elemetalist"""
        magic = self._check_potion(POTION_USE_LIST)
        if magic:
            df = pd.DataFrame(DICT_NAME_USE_POTIONS)
            sorted_df = self._create_sorted_df(df, magic)
            self._using(sorted_df)

    def _heal_hp(self) -> None:
        """ONLY MAG HEAL!!!! Add heal to request"""
        self.ina += "320@"
        self.my_od -= 30
        text = f"{NICKNAME} _heal_hp {self.my_hp=} {self.my_all_hp=}"
        logger.debug(text)

    def _read_json(self) -> None:
        """Create all dict_hits"""
        dir_path = Path(__file__).parent.resolve()
        file_name = "hit_dict_new"
        file_path = os.path.join(dir_path, "settings", f"{file_name}.json")

        with open(file_path, "r", encoding="utf8") as file:
            self.dict_hit = json.loads(file.read())

    def _check_use_hp(self) -> None:
        """Check and use HP"""
        if self.fight_config.HP:
            need_hp = self._conditions_heal(self.my_all_hp, needed_percent=self.fight_config.NEED_HP_PERCENT)
            logger.warning(f"{need_hp=}")
            if self._heal_check(self.my_hp, need_hp):
                self._heal_hp()

    def _check_use_mp(self) -> None:
        """Check and use MP"""
        if self.fight_config.MP:
            logger.warning(f"{self.my_all_mp=}")

            need_mp = self._conditions_heal(self.my_all_mp, need=self.fight_config.NEED_MP_COUNT)
            logger.warning(f"{need_mp=}")
            if self._heal_check(self.my_mp, need_mp):
                logger.error(f"\n{need_mp=} {self.my_mp=}\n")
                self._heal_mp()

    def _check_use_stable_mag_hit(self) -> None:
        """Check need use or not
        Check MP and use or not stable mag hit
        """
        min_mp_coefficient = self.fight_config.MIN_MP_COEFFICIENT
        min_mp_for_hits = self.my_all_mp * min_mp_coefficient

        self.hit = pd.DataFrame()

        if self.my_mp > min_mp_for_hits:
            if self.fight_config.STABLE_MAGIC_HIT:
                stable_magic_hit = self._prepares_stable_magic_hit()
                self.hit = pd.DataFrame(stable_magic_hit).sort_values(by="priority")
        else:
            text = f"{NICKNAME} Not enough MP for mag hit {self.my_mp} < {min_mp_for_hits}"
            logger.warning(text)

    def _check_use_stable_hit(self) -> None:
        """Check need use or not stable hit"""
        if self.fight_config.STABLE_HIT:
            stable_hit = self._prepares_stable_hit()
            if self.hit.empty:
                self.hit = pd.DataFrame(stable_hit).sort_values(by="priority")

    def _check_use_kick(self) -> None:
        """Check use or not kick and use"""
        kick = []
        if self.bot_name != PLAGUE_ZOMBIE:
            kick = deepcopy(KICK)
            if PERSON_TYPE == MAG:
                if SAND_WALL in kick:
                    kick.remove(SAND_WALL)
        else:
            kick = KICK
        if self.fight_config.KICK:
            self._use_kick(kick)

    def _check_use_scroll(self) -> None:
        """Check use or not scroll and use"""
        if self.fight_config.SCROLL:
            if self.scroll:
                self._use_scroll(HIT_SCROLLS[5])

    def _init_fight_config(self, *, zombie: bool = False) -> None:
        """Initializing fight_config"""
        config = None
        bot_group = None

        if PERSON_ROLE == SLAVE:
            file_name = f"fight_config_{PERSON_ROLE}"
        else:
            file_name = f"fight_config_{PERSON_ROLE}_{PERSON_TYPE}"
        logger.critical(f"{file_name=}")
        fight_conf = get_fight_config(file_name)
        for element in fight_conf:
            if self.bot_name in element["names"]:
                bot_group = element
                if zombie:
                    config = element["level"].get("zombie")
                    logger.warning(f"Set zombie {config=}")
                    break
                for key, value in element["level_group"].items():
                    if self.bot_level in value:
                        config = element["level"].get(key)
                        break
                break

        if not config:
            if bot_group:
                config = bot_group["level"].get("default")
                logger.warning(f"Set default {config=}")

        if config:
            self.fight_config = FightConfig(**config)
        else:
            text = f"{NICKNAME} Fight config not found. {self.bot_name=} Use default!!!"
            logger.critical(text)
            send_telegram(text)
            self.fight_config = FightConfig()

    def use_block(self) -> None:
        """Check use or not scroll and use"""
        self.my_od -= 45
        self.inb += "0_29_20"

    def _init_config(self, *, zombie: bool = False) -> None:
        """int config"""
        self._init_fight_config(zombie=zombie)

        self._check_use_hp()

        self._check_use_mp()

        self.strong_potion()

        if zombie and PERSON_TYPE == MAG:
            self.use_block()

        logger.trace(f"{self.magic_in=}")

        self._check_use_stable_mag_hit()

        self._check_use_stable_hit()

        self._check_use_scroll()

    def _prepares_stable_hit(self) -> dict:
        """Create stable_hit dict to DF"""
        hit_od = self.simple_hit_od
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
        mp_hit = self.fight_config.MP_HIT
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

    def fight(self, *, zombie: bool = False) -> None:
        """Start fight"""
        self._all_info()

        self._init_config(zombie=zombie)

        self._get_hit()

        self._check_use_kick()

        self._get_query()

    def _all_info(self) -> list[str]:
        """Get info on console log"""
        number = 2
        hp_bots = []
        len_lives_g1 = len(self.lives_g1)
        if len_lives_g1 % 5 == 0:
            value = self.lives_g1
            max_number_iter = int(len_lives_g1 / 5)
        else:
            max_number_iter = int(len(self.lives_g2) / 5)
            value = self.lives_g2
        for _ in range(max_number_iter):
            hp_bots.append(value[number])
            number += 5
        text = f"hp_bots = {hp_bots}"
        logger.info(text)
        text2 = f"bot_name = {self.bot_name}"
        logger.success(text2)
        return hp_bots

    def _conditions_heal(self, maximum: int, needed_percent: float = None, need: float = None) -> float:
        """Get value for minimum hp or mp

        :param maximum: maximum value
        :type maximum: int
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
        elif need:
            return need

    def _use_scroll(self, scroll: str) -> None:
        """Add scroll to request"""
        self._convert_name_to_value(scroll)
        if self.my_od >= (30 + self.item_od):
            for num, element in enumerate(self.magic_in):
                if self.item_value == element:
                    self.ina += f"{self.item_value}_{self.alchemy[num]}@"
                    self.my_od -= self.item_od

    def _convert_name_to_value(self, name: str) -> None:
        """Create new attributes"""
        self.item_value = str(self.dict_hit.get(name)["number"])
        self.item_od = int(self.dict_hit.get(name)["od"])
        self.item_mp = int(self.dict_hit.get(name)["mp"])

    def _use_kick(self, kicks: list[str]) -> None:
        """Add powered hit this is use mag buff
        or it can be used of warrior top hit"""
        count = self.fight_config.KICK_COUNT
        for item in kicks:
            if count:
                self._convert_name_to_value(item)
                if self.my_od >= self.item_od:
                    if self.item_value in self.magic_in:
                        if f"{self.item_value}@" not in self.ina:
                            self.ina += f"{self.item_value}@"
                            self.my_od -= self.item_od
                            count -= 1
                            text = f"using KICK {self.item_value=}"
                            logger.debug(text)

    def _get_hit(self) -> None:
        """Create hit for the current turn"""
        if PERSON_TYPE == MAG and self.my_mp > 300:
            self._check_in_prof_hits()
            self._preparation_big_hit()
        elif PERSON_TYPE == WARRIOR:
            self._check_in_prof_hits()
            self._preparation_big_hit()

        self._preparation_small_hit()

        self._aggregate_df_hits()

    def _check_in_prof_hits(self) -> None:
        """Check super hit and create sorted DF"""
        self.hits_df = pd.DataFrame()
        if self.fight_config.SUPER_HIT:
            all_hits_df = pd.DataFrame(ANY_PROF_HITS)
            for element in self.magic_in:
                self.hits_df = pd.concat(
                    [self.hits_df, all_hits_df[all_hits_df["code"] == int(element)]], ignore_index=True
                )

        if self.hits_df.empty:
            logger.info("cooldown magic hit skills")
            self._check_use_kick()
        else:
            self.hits_df = self.hits_df.sort_values(by="priority")

    def _preparation_big_hit(self) -> None:
        """Prepare big hit"""
        first_hit_boost_od = 0
        second_hit_boost_od = 25
        third_hit_boost_od = 50
        od_dict = {0: first_hit_boost_od, 1: second_hit_boost_od, 2: third_hit_boost_od}
        num_iteration = 3

        if not self.hits_df.empty:
            for iteration in range(num_iteration):
                for num in self.hits_df["od"].index:
                    if self.hits_df["name"][num] == "Цепная молния":
                        continue

                    od = od_dict.get(iteration) + self.hits_df["od"][num]
                    if self.my_od >= int(od):
                        if iteration:
                            # TODO
                            # BUG
                            if self.hits_df["code"][num] != element:
                                break
                        element = self.hits_df["code"][num]
                        self.my_od -= od
                        self.list_hits.append(element)
                        break

    def _preparation_small_hit(self) -> None:
        """Prepare small hit"""
        first_hit_boost_od = 0
        second_hit_boost_od = 25
        third_hit_boost_od = 50
        if self.list_hits:
            have_count = len(self.list_hits)
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
            if not self.hit.empty:
                for num in self.hit["od"].index:
                    od = od_dict.get(iteration) + self.hit["od"][num]
                    if self.my_od >= int(od):
                        element = self.hit["code"][num]
                        self.my_od -= od
                        self.list_hits.append(element)
                        break

    def _aggregate_df_hits(self) -> None:
        """Aggregate DF hits"""
        self.aggregate_hits = pd.concat([self.hits_df, self.hit], ignore_index=True)

    def _get_query(self) -> None:
        """
        Create query part 'inu'
        """
        for num, value in enumerate(self.list_hits):
            mp = self.aggregate_hits[self.aggregate_hits["code"] == value].iloc[0]["mp_cost"]
            self.inu += f"{num}_{value}_{mp}@"

    def get_queries_param(self) -> Hit:
        """Get query hit prams"""
        data = {"inu": self.inu, "inb": self.inb, "ina": self.ina}
        return Hit(**data)

    def get_data(self) -> dict[str, str]:
        """Get query data
        It can return dict with retry
        """
        if self.stop:
            return {"retry": "True"}
        data = {
            "post_id": "7",
            "vcode": self.fight_pm[4],
            "enemy": self.fight_pm[5],
            "group": self.fight_pm[6],
            "inf_bot": self.fight_pm[7],
            "inf_zb": self.fight_pm[10],
            "lev_bot": self.param_en[5],
            "ftr": self.fight_ty[2],
            "inu": self.inu,
            "inb": self.inb,
            "ina": self.ina,
        }
        return data
