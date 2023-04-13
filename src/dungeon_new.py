import json
import random
import re
import time
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from decimal import ROUND_UP
from typing import Union

from loguru import logger

import upivka

from logic.implementation import create_right_way
from logic.implementation import find_lists_ways_slave
from logic.implementation import find_near_way
from logic.implementation import find_near_way_slave
from logic.implementation import find_way_to
from logic.implementation import find_way_to_slave
from logic.implementation import uncharted_path
from logic.implementation import uncharted_path_slave
from logic.implementation import down
from logic.implementation import right
from logic.implementation import left
from logic.implementation import up

from config.config_scroll import AGREE
from config.config_scroll import Teleport

from config.check_effects import Effects

from config.config_potion import COUNT_POTION
from config.config_potion import NEED_POTIONS

from config.pattern import FIND_VAR_EFF
from config.pattern import FIND_POS_VARS
from config.pattern import FIND_POS_MANA
from config.pattern import FIND_POS_TYPE
from config.pattern import FIND_POS_OCHD
from config.pattern import FIND_USE
from config.pattern import FIND_STRING_WITH_QUERY
from config.pattern import FIND_FIRST_PART
from config.pattern import FIND_SECOND_PART
from config.pattern import FIND_INSHP
from config.pattern import FIND_VAR_OBJ_ACTION
from config.pattern import FIND_OBJ_ACTION
from config.pattern import FIND_TELEPORT
from config.pattern import FIND_FRAME
from config.pattern import FIND_IN_CITY
from config.pattern import FIND_FEXP
from config.pattern import FIND_PARAM_OW
from config.pattern import FIND_STATS
from config.pattern import FIND_PAGE_INVENTAR
from config.pattern import FIND_SCROLL_STRIKE_FURY
from config.pattern import FIND_FROM_NATURE_TO_INV

from config.urls import URL
from config.urls import URL_MAIN
from config.urls import URL_PLAYER_INFO
from config.urls import URL_EVENT
from config.urls import URL_KEEP_CONNECTION

from config.config_heal import DUNGEON_MP_HEALING_BEFORE_BOT
from config.config_heal import DUNGEON_MP_HEALING_BEFORE_BOSS
from config.config_heal import DUNGEON_HP_HEALING_BEFORE_BOT
from config.config_heal import DUNGEON_HP_HEALING_BEFORE_BOSS
from config.config_heal import DUNGEON_MP_NEED_BEFORE_BOSS_FOR_WARRIOR
from config.config_heal import DUNGEON_MP_NEED_BEFORE_BOSS_FOR_MAG
from config.config_heal import DUNGEON_HP_HEALING_BEFORE_BOSS_POTION_HP
from config.config_heal import DUNGEON_HP_HEALING_BEFORE_BOSS_POTION_MP
from config.config_heal import MP_LIST_MP

from heal.healing_potion_name import ENERGY_POTION
from heal.healing_potion_name import EXCELLENT_HEALING_POTION
from heal.healing_potion_name import EXCELLENT_MANA_POTION

from config.local_config import AB
from config.local_config import SIEGE_DRESS
from config.local_config import TELEPORT_CITY
from config.local_config import CITY
from config.local_config import AUTO_BUFF
from config.local_config import FLOOR
from config.local_config import LOGIN
from config.local_config import NICKNAME
from config.local_config import PROXY
from config.local_config import PROXIES
from config.local_config import PROXY_IP
from config.local_config import SLEEP_TIME
from config.local_config import FIGHT_TEST_MODE
from config.local_config import FIGHT_ITERATIONS
from config.local_config import LEN_PARTY
from config.local_config import SLEEP_TIME_PER_HIT
from config.local_config import PERSON_ROLE
from config.local_config import PERSON_TYPE
from config.local_config import SIEGE
from config.local_config import MAG_DAMAGER
from config.local_config import LEADER_TYPE
from config.local_config import MAG_KILLER
from config.local_config import PARTY_MEMBERS
from config.local_config import LEADER_NAME

from bots.bot_names import PLAGUE_ZOMBIE

from bots.bot_type import DUNGEON_BOSSES
from bots.bot_type import DUNGEON_BOSSES_AND_BOTS
from bots.bot_type import DUNGEON_MAG_BOSSES
from bots.bot_type import DUNGEON_WARRIOR_BOSSES

from config.variable_names import SLAVE
from config.variable_names import SOLO
from config.variable_names import LEADER
from config.variable_names import WARRIOR
from config.variable_names import MAG

from fight import Fight

from request import Connection
from request import my_ip
from request import send_telegram

from location.classes import Location


class Game:
    def __init__(self) -> None:

        self.my_mp = 5_000
        self.my_hp = 5_000

        self.init_connection()

        self.fight_class: Fight = Fight()

        logger.success("__init__")

    def get_page_text(self) -> str:
        return self.connect.get_html_page_text()

    def init_connection(self) -> None:
        self.nickname = NICKNAME
        if PROXY:
            self.ip = my_ip(PROXIES)
        else:
            self.ip = my_ip()

        if PROXY_IP in self.ip:
            logger.info(f"\n-------ip------- {self.ip} LOGIN {self.nickname}" * 5)

        self.connect = Connection(PROXY)

    def _find_pattern(self, pattern: str, string: str = None) -> list:
        if string:
            return re.findall(pattern, string)
        return re.findall(pattern, self.connect.get_html_page_text())

    def check_live(self) -> None:
        """Check live status in battle"""
        result = self._find_pattern(FIND_PARAM_OW)
        if result:
            new_result: str = result.pop()
            param_ow = new_result.replace("]", "").replace('"', "").replace("[", "").split(",")
            if param_ow[1] == "0":
                text_for_message = f"{NICKNAME} YOU KILLED BUT FIGHT NOT ENDED"
                logger.error(text_for_message)
                send_telegram(text_for_message)
                raise Exception(text_for_message)

    def create_data_end_battle(self, fexp: list[str]) -> dict[str, str]:
        """Create data to end battle in battle"""
        # # TODO: протестить в подземке
        text_for_message = f"{NICKNAME} END BATTLE"
        logger.info(text_for_message)
        return {
            "get_id": "61",
            "act": "7",
            "fexp": fexp[0],
            "fres": fexp[1],
            "vcode": fexp[3],
            "ftype": fexp[5],
            "min1": fexp[8],
            "max1": fexp[9],
            "min2": fexp[10],
            "max2": fexp[11],
            "sum1": fexp[12],
            "sum2": fexp[13],
        }

    def check_end_battle(self) -> dict[str, str] | None:
        """Check end battle in battle"""
        result: list[str] = self._find_pattern(FIND_FEXP)
        if result:
            new_result: str = result.pop()
            fexp: list[str] = new_result.replace("]", "").replace('"', "").replace("[", "").split(",")
            return self.create_data_end_battle(fexp)
        return None

    def logic(self) -> dict[str, str]:
        """
        this bloc may change
        """
        my_od, my_mp, my_hp = self.fight_class.get_state()
        self.my_mp = my_mp
        self.my_hp = my_hp

        self.fight_class.fight()
        data = self.fight_class.get_queries_param()
        inu = data.inu
        inb = data.inb
        ina = data.ina

        part1 = f"inu-{inu} inb-{inb} ina-{ina}"
        part2 = f" my_od-{my_od} my_mp-{my_mp}"
        part3 = f" my_hp-{my_hp}"
        text = part1 + part2 + part3
        logger.debug(text)
        return self.fight_class.get_data()

    def parse_fight(self, fight_iteration: int) -> dict[str, str]:
        """Parse FIGHT"""
        self.check_live()
        data = self.check_end_battle()  # check and if True create data
        if data:
            return data

        # self.fight_class.setup_value(self.connect)
        # # TODO: Этот код может работать только в подземке
        # value_m = self.js_obj.get("m")
        # logger.debug(f"message={value_m}")
        # if "Невозможно добавить атакующего в бой" in value_m:
        #     logger.error("Невозможно добавить атакующего в бой.")
        #     send_telegram("Невозможно добавить атакующего в бой.")
        # if "Глубокий порез" in value_m:
        #     logger.error("Невозможно добавить атакующего в бой.")
        #     send_telegram("Невозможно добавить атакующего в бой.")

        self.fight_class.setup_value(self.connect.get_html_page_text(), fight_iteration)

        for player, value in self.fight_class.check_log().items():
            logger.critical(f"player type={type(player)=} value type={type(value)=}")
            logger.critical(f"{player=} {value=}")
            if damage := value.get("damage"):
                logger.debug(f"self.zombie_hit[player] = damage   {player=}  {damage=}")
                self.zombie_hit[player] = damage

        data = self.logic()
        return data

    def stop_or_hit(self, fight_iteration: int) -> None:
        data = self.parse_fight(fight_iteration)
        if PERSON_ROLE == SLAVE:

            # TODO change enemy
            # logger.critical(f"BEFORE .........{self.fight_class.fight_pm[9]=}")
            # if cenemy := self.fight_class.fight_pm[9]:
            #     logger.critical(f"{self.fight_class.bot_hp=} {self.fight_class.bot_name=}")
            #     logger.critical("Change enemy")
            #     self.connect.get_html(URL_MAIN, data={"cenemy": cenemy})
            #     logger.critical("parse_fight one more time")
            #     data, boss = self.parse_fight(fight_iteration)
            #     logger.critical(f"{self.fight_class.bot_hp=} {self.fight_class.bot_name=}")

            self.continue_fight = True
            if "post_id" in data.keys():
                bot_name = self.fight_class.get_bot_name()
                if bot_name in DUNGEON_MAG_BOSSES:
                    self.mag_boss = True
                if not self.zombie_hit.get(self.nickname):
                    if bot_name == PLAGUE_ZOMBIE:
                        if MAG_KILLER and self.mag_boss:
                            logger.info(f"Wait. because this is zombie and {self.nickname} is MAG_KILLER")
                        else:
                            logger.info(f"This must be first hit by {self.nickname}")
                            self.connect.post_html(URL_MAIN, data)
                            self.fight_class.setup_value(self.connect.get_html_page_text(), fight_iteration)
                            for player, value in self.fight_class.check_log().items():
                                if self.nickname == player:
                                    if damage := value.get("damage"):
                                        self.zombie_hit[player] = damage
                    else:
                        logger.info(f"Wait. because this is boss {self.nickname}")
                else:
                    # BUG need delete log
                    logger.debug(f"{self.zombie_hit=}")
                    if bot_name == PLAGUE_ZOMBIE:
                        if all(self.zombie_hit.values()):
                            if MAG_KILLER and self.mag_boss:
                                logger.info(f"Wait. because this is zombie and {self.nickname} is MAG_KILLER")
                            else:
                                self.connect.post_html(URL_MAIN, data)
                                logger.info(
                                    f"All players hit zombie. Not the first strike on zombies by {self.nickname}"
                                )
                        else:
                            logger.info(f"Wait. not all players hit zombie {self.nickname}")
                    else:
                        if MAG_KILLER and self.mag_boss and all(self.zombie_hit.values()):
                            logger.info(f"Hit boss. because this is MAG_KILLER {self.nickname}")
                            self.connect.post_html(URL_MAIN, data)
                        else:
                            logger.info(f"{all(self.zombie_hit.values())=}")
                            logger.info(f"Wait. because this is boss {self.nickname} and not all do hit")
            else:
                # This is and of battle
                if SIEGE:
                    # This is and of battle. Fight stopped!!! NEED see logs
                    text = f"{NICKNAME} {SIEGE} fight stopped!!! NEED see logs"
                    send_telegram(text)
                    raise Exception(text)
                logger.info("Get a request for the end battle")
                self.connect.get_html(URL_MAIN, data)
                self.continue_fight = False
        else:
            if "post_id" in data.keys():
                # TODO liader do hit!
                self.connect.post_html(URL_MAIN, data)
                self.continue_fight = True
            elif "retry" in data.keys():
                logger.debug("retry")
                # self.connect.get_html(URL_MAIN)
                self.continue_fight = True
            else:
                # This is and of battle
                if SIEGE:
                    # This is and of battle. Fight stopped!!! NEED see logs
                    text = f"{NICKNAME} {SIEGE} fight stopped!!! NEED see logs"
                    send_telegram(text)
                    raise Exception(text)
                logger.info("Get a request for the end battle")
                self.connect.get_html(URL_MAIN, data)
                self.continue_fight = False

    def check_not_error(self):
        pattern = r"error.css"
        error = self._find_pattern(pattern)
        if error:
            logger.trace("NEED RELOGIN!!!")
            logger.trace("DO RELOGIN!!!")
            logger.trace("DO RELOGIN!!!")
            self.init_connection()

    def run_fight(self) -> None:
        def check_iter(fight_iteration: int, start_time: float) -> float:
            logger.info(f"fight_iteration - '{fight_iteration}'")
            if fight_iteration % 50 == 0:
                text = f"{NICKNAME} ----TOO LONG FIGHT---- >= {fight_iteration}"
                logger.error(text)
                send_telegram(text)
            logger.debug(f"iter_time - {time.perf_counter() - start_time}")
            return time.perf_counter()

        fight_iteration = 0
        start_time = time.perf_counter()

        self._init_zombie_hit()
        self.mag_boss = False
        # TODO add условие о том что это маг босс
        try:
            room_bots = self.js_obj["s"].get("roomBots", False)
            logger.debug(f"{room_bots=}")
            if room_bots:
                bots_name = room_bots[0].get("nickname")
            else:
                bots_name = "NO"
                # BUG
                logger.critical(f"{bots_name=}")
        except Exception:
            bots_name = "NO"
            logger.critical(f"{bots_name=}")
        logger.debug(f"{bots_name=}")
        if bots_name in DUNGEON_MAG_BOSSES:
            self.zombie_hit[MAG_DAMAGER] = True
        else:
            self.zombie_hit[LEADER_NAME] = True

        self.full_fight = not FIGHT_TEST_MODE
        if self.full_fight:
            logger.success(f"{self.full_fight=}")
            self.continue_fight = self.full_fight
            while self.continue_fight:
                # # BUG off chat
                # self.get_chat()
                self.check_not_error()
                self.stop_or_hit(fight_iteration)
                if PERSON_ROLE == SLAVE:
                    if SIEGE:
                        text = "----FIGHT---- no delay"
                        logger.error(text)
                    else:
                        text = f"----FIGHT---- ALL players made a move and SLEEP = {SLEEP_TIME_PER_HIT} seconds"
                        logger.error(text)
                        time.sleep(float(SLEEP_TIME_PER_HIT))
                        # self.connect.get_html(URL_MAIN)
                else:
                    # text = "----FIGHT---- delay 0.4"
                    text = "----FIGHT---- no delay"
                    logger.error(text)
                    # time.sleep(float(0.4))
                self.connect.get_html(URL_MAIN)
                fight_iteration += 1
                start_time = check_iter(fight_iteration, start_time)
        else:
            logger.success(f"{self.full_fight=}")
            while fight_iteration < FIGHT_ITERATIONS:
                self.stop_or_hit(fight_iteration)
                if PERSON_ROLE == SLAVE:
                    if SIEGE:
                        text = "----FIGHT---- no delay"
                        logger.error(text)
                    else:
                        text = f"----FIGHT---- ALL players made a move and SLEEP = {SLEEP_TIME_PER_HIT} seconds"
                        logger.error(text)
                        time.sleep(float(SLEEP_TIME_PER_HIT))
                else:
                    # text = "----FIGHT---- delay 0.4"
                    text = "----FIGHT---- no delay"
                    logger.error(text)
                    # time.sleep(float(0.4))
                fight_iteration += 1
                start_time = check_iter(fight_iteration, start_time)
        self.connect.get_html(URL_MAIN)

    def game(self) -> str:
        try:
            self.js_obj = json.loads(self.connect.get_html_page_text())
            text = "Expected get_html_page_text == json and it is True"
            logger.success(text)
        except json.decoder.JSONDecodeError:
            text = "Expected get_html_page_text == json BUT IT IS NOT"
            logger.warning(text)
            self.get_status()

        if PERSON_ROLE != SLAVE:
            self.is_attack()
        self.floor = self.is_floor()

        for _ in range(5):
            text = f"Start floor - '{self.floor:.^20}'"
            logger.success(text)

        self._dungeon_while()

        text = f"{NICKNAME} All Done"
        send_telegram(text)
        return text

    def is_attack(self) -> None:
        """
        Check the presence of an enemy and attack
        Take items
        """
        if vcode := self.js_obj["a"].get("attack"):
            data = {
                "type": "dungeon",
                "action": "attack",
                "vcode": vcode,
                "r": random.random(),
            }
            self.connect.post_html(URL_EVENT, data)
            self.connect.get_html(URL_MAIN)
            self.run_fight()
            self.get_status()
            if PERSON_ROLE != SLAVE:
                self.check_pickup()
                self.check_pickup()
        else:
            if PERSON_ROLE != SLAVE:
                self.check_pickup()
                self.check_pickup()
        text = self.string_info()
        logger.info(f"after fight {text}")

    def string_info(self) -> str:
        """
        Create string to debug log
        """
        coord_x = self.js_obj["s"]["x"]
        coord_y = self.js_obj["s"]["y"]
        way_to_go = self.js_obj["s"]["map"][self.js_obj["s"]["x"]][self.js_obj["s"]["y"]].get("p")
        oil = self.is_oil()
        oil_price = self.js_obj["s"]["oilPrice"]
        self.floor = self.is_floor()
        if self.js_obj["s"]["own"]:
            key = True
        else:
            key = False
        buttons = self.js_obj["s"].get("buttonsLeft")
        doors = False

        # room_bots = self.js_obj["s"].get("roomBots", False)
        # if room_bots:
        #     bots_name = room_bots[0].get("nickname")
        #     if bots_name in DUNGEON_MAG_BOSSES:
        #         message = f"\n\n --- {NICKNAME} {bots_name} --- \n"
        #         logger.debug(message)
        #         if PERSON_ROLE == LEADER and PERSON_TYPE == WARRIOR:
        #             send_telegram(message)

        cell = self.js_obj["s"]["map"][coord_x][coord_y]
        if cell.get("chest"):
            text = f"\n\n --- {NICKNAME} chest yes = {cell.get('chest')} {self.floor=}--- \n"
            logger.success(text)
            send_telegram(text)
        if cell.get("bots"):
            text = f"\n\n --- {NICKNAME} bots on cell = {cell.get('bots')} --- \n"
            logger.info(text)
            # send_telegram(text)

        text = f"oil- '{oil}' oilPrice- '{oil_price}' floor- '{self.floor}'"
        text += f" coord= '{coord_x}{coord_y}' '{way_to_go}'"
        text += f" key= '{key}' buttons= '{buttons}'"
        for num_x, row in enumerate(self.js_obj["s"]["map"]):
            for num_y, _ in enumerate(row):
                exist = self.js_obj["s"]["map"][num_x][num_y]
                if exist:
                    if exist.get("doors"):
                        doors = True
        text += f" doors= '{doors}'"
        return text

    def is_alive(self) -> int:
        """
        Alive=1  Dead=0
        """
        return self.js_obj["s"]["alive"]

    def is_floor(self) -> int:
        """
        Number floor
        """
        return self.js_obj["s"]["floor"]

    def is_oil(self) -> int:
        """
        Count oil
        """
        return self.js_obj["s"]["oil"]

    def check_pickup(self) -> None:
        """
        Take items
        """
        for key in self.js_obj["a"].keys():
            if key.find("pickup") != -1:
                item = key.replace("pickup.", "")
                vcode = self.js_obj["a"].get(key)
                data = {
                    "type": "dungeon",
                    "action": "pickup",
                    "item": item,
                    "vcode": vcode,
                    "r": random.random(),
                }

                self.connect.post_html(URL_EVENT, data)
                self.update_json()

                coord_x = self.js_obj["s"]["x"]
                coord_y = self.js_obj["s"]["y"]
                elem_v = self.js_obj["s"]["map"][self.js_obj["s"]["x"]][self.js_obj["s"]["y"]].get("v")

                text = f"pick up something info: x={coord_x} y={coord_y} v={elem_v}"
                logger.success(text)

    def _set_default_variable(self) -> None:
        """Set default values for attributes"""
        self.portal: bool = False
        self.doors: bool = False
        self.buttons: bool = False
        self.key: bool = False
        self.reward: bool = False
        self.boss: bool = False
        self.way_to_door: list = list()
        self.way_to_port: list = list()

    def _dungeon_while(self) -> None:
        while self.floor < int(FLOOR):
            self.floor = self.is_floor()
            self._check_auto_buff()
            self._set_default_variable()
            self.iter_number = 0
            logger.info(f"-----------iter number '{self.iter_number}'----------------")
            text = self.string_info()
            logger.info(text)

            if PERSON_ROLE == SLAVE:
                self._new_while_slave()
            else:
                self._new_while()

    def check_portal(self) -> None:
        """
        Checks if the portal is found?
        """
        if not self.portal:
            for num_x, coord_x in enumerate(self.js_obj["s"]["map"]):
                for num_y, _ in enumerate(coord_x):
                    exist = self.js_obj["s"]["map"][num_x][num_y]
                    if exist:
                        if exist.get("v") == 11:
                            self.portal = True

    def check_key_new(self) -> None:
        """
        Checks if the key is found?
        """
        if not self.key:
            if self.js_obj["s"]["own"]:
                self.key = True

    def check_buttons(self) -> None:
        """
        Checks if the buttons is found?
        """
        if not self.buttons:
            number = self.js_obj["s"].get("buttonsLeft")
            if number == 0:
                self.buttons = True

    def check_doors(self) -> None:
        """
        Checks if the doors is found?
        """
        if not self.doors:
            for num_x, coord_x in enumerate(self.js_obj["s"]["map"]):
                for num_y, _ in enumerate(coord_x):
                    exist = self.js_obj["s"]["map"][num_x][num_y]
                    if exist:
                        if exist.get("doors"):
                            self.doors = True
                            [coord] = exist.get("doors").keys()
                            neighbors = {
                                "u": up,
                                "r": right,
                                "d": down,
                                "l": left,
                            }
                            self.coord_doors = f"{neighbors[coord](num_x, num_y)}"

    def check_reward(self) -> None:
        """
        Checks if the reward gotten?
        """
        if not self.reward:
            for num_x, coord_x in enumerate(self.js_obj["s"]["map"]):
                for num_y, _ in enumerate(coord_x):
                    cell_exist = self.js_obj["s"]["map"][num_x][num_y]
                    if cell_exist:
                        if cell_exist.get("doors"):
                            [coord] = cell_exist.get("doors").keys()
                            # new_result: str = result.pop()
                            neighbors = {
                                "u": up,
                                "r": right,
                                "d": down,
                                "l": left,
                            }
                            coord_reward = f"{neighbors[coord](num_x, num_y)}"
                            rew_x = int(coord_reward[0])
                            rew_y = int(coord_reward[1])
                            reward_exist = self.js_obj["s"]["map"][rew_x][rew_y]
                            if reward_exist:
                                self.reward = True

    def check_reward_and_boss(self) -> None:
        """
        Checks it is chest?
        """
        coord_x = self.coord_doors[0]
        coord_y = self.coord_doors[1]
        cell_door = self.js_obj["s"]["map"][int(coord_x)][int(coord_y)]
        if cell_door:
            logger.debug("reward check")
            logger.debug(f"cell_door.get('bots') = {cell_door.get('bots')}")
            logger.debug(f"cell_door.get('chest') = {cell_door.get('chest')}")
            if cell_door.get("chest"):
                logger.debug(f"set reward True = {cell_door.get('chest')}")
                self.reward = True
            else:
                if not cell_door.get("bots"):
                    logger.debug(f"TEST if not cell_door.get('bots') {self.reward=}")
                    # it's mean that boss are killed
                    self.reward = True
                    self.boss = False  # this is test!!!!!
                if cell_door.get("bots"):
                    self.boss = True
        logger.debug(f"{self.reward=} {self.boss=}")

    def get_hp_mp(self) -> dict:
        """Return HP MP and maximum HP MP"""
        result: list = self._find_pattern(FIND_INSHP)
        if not result:
            # # TODO: was trouble!!!  THIS IS JSON!!! NEED CONVERT AND NOT FIND ANY THING
            text = f"{self.connect.get_html_page_text()=}"
            logger.error(text)
            if "text/html" not in result.headers["Content-Type"]:
                res = self.connect.get_html_page_json()
                logger.error(f"{type(res)} {res=}")
            text = f"{NICKNAME} See in LOGS!!!"
            send_telegram(text)
            raise Exception(text)
        else:
            new_result: str = result.pop()
            result = new_result.replace("]", "").replace('"', "").replace("[", "").split(",")
            hp_mp = {
                "my_max_hp": int(result[1]),
                "my_max_mp": int(result[3]),
                "my_hp": int(result[0]),
                "my_mp": int(result[2]),
            }
        return hp_mp

    def restoring_hp(self, data: dict, healing: float) -> None:
        """
        Check HP and restore
        """
        logger.critical(f"restoring_hp = {healing=}  {data=}")
        my_max_hp = data["my_max_hp"]
        my_hp = data["my_hp"]
        min_hp = my_max_hp * healing
        try:
            key = EXCELLENT_HEALING_POTION  # Превосходное Зелье лечения
            self.js_obj["a"][key]
        except Exception:
            key = ENERGY_POTION  # Зелье Энергии
        if key == ENERGY_POTION:
            divider = 100
        else:
            divider = 500
        if my_hp <= min_hp:
            count = int(Decimal((min_hp - my_hp) / divider).quantize(Decimal("1")))
        else:
            count = 0
        if count > 0:
            logger.error(f"{my_hp=}")
            logger.error(f"{min_hp=}")
            logger.error(f"{my_max_hp=}")
            logger.error(f"{divider=}")
            self.using_potion(count, key)
        else:
            logger.error(f"Not use HP count = {count}")
            self.get_status()

    def restoring_mp(self, data: dict, healing: float) -> None:
        """
        Check HP and restore
        """
        logger.critical(f"restoring_mp = {healing=}  {data=}")
        my_max_mp = data["my_max_mp"]
        my_mp = data["my_mp"]
        min_mp = my_max_mp * healing
        key = DUNGEON_HP_HEALING_BEFORE_BOSS_POTION_MP  # Превосходное Зелье Маны
        if key == ENERGY_POTION:
            divider = 100
        else:
            divider = 500
        if my_mp <= min_mp:
            count = int(Decimal((min_mp - my_mp) / divider).quantize(Decimal("1"), rounding=ROUND_UP))
        else:
            count = 0
        if count > 0:
            logger.error(f"{my_mp=}")
            logger.error(f"{min_mp=}")
            logger.error(f"{divider=}")
            self.using_potion(count, key)
        else:
            logger.error(f"Not use MP count = {count}")
            self.get_status()

    def going(self, way: str) -> None:
        """
        Make request to go
        :param: way [str] like 'moveDown'
        """
        self.get_chat()
        # self.connect.get_html(URL_MAIN)
        self.get_status()
        oil = self.is_oil()
        alive = self.is_alive()
        if alive == 0 or oil == 0:
            text = f"{NICKNAME} Can't move oil - {oil} alive - {alive}"
            logger.error(text)
            send_telegram(text)
            raise Exception(text)
        if vcode := self.js_obj["a"].get(way):
            action_lst = self._find_pattern(FIND_FIRST_PART, way)
            action: str = action_lst.pop()
            direction_lst = self._find_pattern(FIND_SECOND_PART, way)
            direction: str = direction_lst.pop()
            data = {
                "type": "dungeon",
                "action": action,
                "direction": direction.lower(),
                "vcode": vcode,
                "r": random.random(),
            }
            self.connect.post_html(URL_EVENT, data=data)
            try:
                self.update_json()
            except Exception as error:
                logger.info(f"NOT NEEDED DELETE IT!!! {error}")
            time.sleep(float(SLEEP_TIME))
            try:
                text = self.string_info()
            except Exception as error:
                logger.info(f"after go error!!! {error}")
                raise Exception("See in logs!!!")
            logger.info(f"after go {text}")
            if PERSON_ROLE != SLAVE:
                self.check_pickup()
            if self.js_obj["a"].get("attack"):
                self.connect.get_html(URL_MAIN)
                data = self.get_hp_mp()
                self.restoring_hp(data, DUNGEON_HP_HEALING_BEFORE_BOT)

                self.connect.get_html(URL_MAIN)
                data = self.get_hp_mp()
                self.restoring_mp(data, DUNGEON_MP_HEALING_BEFORE_BOT)

                self.connect.get_html(URL_MAIN)
                self.get_status()
                self.is_attack()
        else:
            self.check_key_new()
            if self.key:
                logger.info("GO TO DOOR IN GOING\n'GO TO DOOR IN GOING'")
                action = "open"
                direction_lst = self._find_pattern(FIND_SECOND_PART, way)
                direction: str = direction_lst.pop()
                new_way = action + direction
                vcode = self.js_obj["a"].get(new_way)
                data = {
                    "type": "dungeon",
                    "action": action,
                    "direction": direction.lower(),
                    "vcode": vcode,
                    "r": random.random(),
                }
                self.connect.post_html(URL_EVENT, data)
                try:
                    self.update_json()
                except Exception as error:
                    logger.info(f"DELETE IT!!!!!!!!!!! {error}")
                vcode = self.js_obj["a"].get(way)
                action_lst = self._find_pattern(FIND_FIRST_PART, way)
                action: str = action_lst.pop()
                direction_lst = self._find_pattern(FIND_SECOND_PART, way)
                direction: str = direction_lst.pop()
                data = {
                    "type": "dungeon",
                    "action": action,
                    "direction": direction.lower(),
                    "vcode": vcode,
                    "r": random.random(),
                }
                self.connect.post_html(URL_EVENT, data=data)
                try:
                    self.update_json()
                except Exception as error:
                    logger.info(f"DELETE IT!!!!!!!!!!! {error}")
                time.sleep(float(SLEEP_TIME))
                try:
                    text = self.string_info()
                except Exception as error:
                    logger.info(f"after go error!!! {error}")
                    raise Exception("FUCK!!!!")
                logger.info(f"after go {text}")
                if PERSON_ROLE != SLAVE:
                    self.check_pickup()
                if self.js_obj["a"].get("attack"):
                    self.connect.get_html(URL_MAIN)
                    data = self.get_hp_mp()
                    self.restoring_hp(data, DUNGEON_HP_HEALING_BEFORE_BOSS)

                    self.connect.get_html(URL_MAIN)
                    logger.info(f"{self.js_obj['a']=}")
                    data = self.get_hp_mp()
                    healing_mp = DUNGEON_MP_HEALING_BEFORE_BOSS  # 0.4
                    need_mp = DUNGEON_MP_NEED_BEFORE_BOSS_FOR_WARRIOR  # Turn  6_000
                    min_mp = data["my_max_mp"] * healing_mp  # 13100 * 0.4 = 5200
                    logger.error(f"min_mp {min_mp} , need_mp {need_mp}")
                    if min_mp < need_mp:
                        healing_mp = need_mp / data["my_max_mp"]
                        # # BUG DO NOT TOUCH THIS
                        # # healing_mp = (data["my_max_mp"] / need_mp) % 1  # (13100 / 6000) = 2.16 % 1 = 0.16
                        # # healing_mp = (need_mp / data["my_max_mp"]) % 1  # (13100 / 6000) = 2.16 % 1 = 0.16
                        if healing_mp > 1:
                            raise Exception(f"healing_mp > 1 {healing_mp=}")
                        logger.error(f"change percent from {DUNGEON_MP_HEALING_BEFORE_BOSS} to {healing_mp}")
                    self.restoring_mp(data, healing_mp)

                    self.connect.get_html(URL_MAIN)
                    self.get_status()
                    self.is_floor()

                    room_bots = self.js_obj["s"].get("roomBots", False)
                    text = f"--- {NICKNAME} --- BOSSSSS --- {self.floor=} --- {room_bots[0].get('nickname', 'Not find')} ---"
                    logger.critical(text)
                    send_telegram(text)

                    self.is_attack()
                    self.boss = True
            else:
                logger.error(f"---- Trouble - NO KEY---'{way.upper()}' --------")
                text = self.string_info()
                logger.error(text)
                message = f"{NICKNAME} STOP ITER Trouble NO KEY BUT DOOR----'{way}'"
                logger.error(message)
                send_telegram(message)
                raise Exception(message)

    def test_while_my_new(self, ways: list[str]) -> None:
        """
        While for ways
        """
        for way in ways:
            self.going(way)
            self.iter_number += 1
            logger.info(f"--iter number '{self.iter_number}'--- way '{way.upper()}'---")

    def going_to_reward(self, coord: list) -> None:
        """
        Go to reward
        :param: coord - list like ["12"]
        """
        self.test_while_my_new(coord)

    def get_coord_portal(self) -> str:
        """
        Find coord portal
        """
        for num_x, coord_x in enumerate(self.js_obj["s"]["map"]):
            for num_y, _ in enumerate(coord_x):
                exist = self.js_obj["s"]["map"][num_x][num_y]
                if exist:
                    port = self.js_obj["s"]["map"][num_x][num_y].get("v")
                    if port == 11:
                        coord = f"{num_x}{num_y}"
        return coord

    def going_to(self, coord: Union[str, list[str]]) -> None:
        """
        Go to coord
        """
        way_to = create_right_way(self.js_obj, coord)
        self.test_while(way_to)

    def test_while(self, ways: list[str]) -> None:
        """
        While for ways
        """
        for way in ways:
            self.going(way)
            self.iter_number += 1
            logger.info(f"--iter number '{self.iter_number}'--- way '{way.upper()}'---")

    def go_while(self, new_set: list) -> None:
        """
        While for ways
        new_set: list   list with ways!!!!!!
        """
        ways = create_right_way(self.js_obj, new_set)
        logger.error(f"go_while {ways=}")
        for way in ways:
            # # TODO: TEST
            # self.get_chat()  # NEED TEST!!!!
            # self.get_status()  # NEED TEST!!!!
            try:
                oil = self.is_oil()
            except Exception as error:
                text = "OIL!!!!"
                logger.error(error)
                # send_telegram(text)
                raise Exception(text)

            if oil == 0:
                text = f"- {self.nickname} Can't move oil - {oil} "
                logger.error(text)
                send_telegram(text)
                raise Exception(text)
            vcode = self.js_obj["a"].get(way)
            logger.debug(f"GO TO {way} {self.nickname}")
            [action] = self._find_pattern(FIND_FIRST_PART, way)
            [direction] = self._find_pattern(FIND_SECOND_PART, way)
            data = {
                "type": "dungeon",
                "action": action,
                "direction": direction.lower(),
                "vcode": vcode,
                "r": random.random(),
            }
            self.connect.post_html(URL_EVENT, data=data)
            try:
                self.update_json()
            except Exception as error:
                logger.debug(f"DONT KNOW {error}")
            # logger.info(f"go_while sleep({SLEEP_TIME})")
            time.sleep(float(SLEEP_TIME))

    def check_right_way(self, income_way) -> None:
        not_visited = uncharted_path_slave(self.js_obj)
        lists_ways = find_lists_ways_slave(self.js_obj, not_visited)
        lists_ways.append(income_way)
        my_set_difference = set(lists_ways[0])
        for ways in lists_ways[1:]:
            my_set_difference.intersection_update(ways)
        max_path_in_steps = max((way for way in lists_ways), key=len)
        right_way = []
        for step in max_path_in_steps:
            if step in my_set_difference:
                my_set_difference.remove(step)
                right_way.append(step)
        if right_way:
            self.go_while(right_way)

    def _new_while_slave(self) -> None:
        next_level = False
        while not next_level:
            # # when connect to chat need get json answer
            self.get_chat()
            self.get_status()
            self.check_key_new()
            self.check_doors()
            if self.doors:
                self.check_reward_and_boss()
            self.check_portal()
            # logger.info(f"portal - {self.portal}")
            text = self.string_info()
            logger.debug(f"After iter {text}")
            info1 = f"INFO!!! portal={self.portal}"
            info2 = f" boss={self.boss}"
            info3 = f" reward={self.reward}"
            info4 = f" doors={self.doors}"
            info5 = f" floor={self.floor}"
            all_info = info1 + info2 + info3 + info4 + info5
            logger.info(all_info)
            if self.portal:
                try:
                    coord_port = self.get_coord_portal()
                    self.way_to_port = find_way_to_slave(self.js_obj, coord_port)
                except UnboundLocalError:
                    logger.error("portal was activated by party leader")
                    break
            if self.boss and not self.reward:
                if self.floor >= 3:
                    self.way_to_door = find_way_to_slave(self.js_obj, self.coord_doors)
                    if len(self.way_to_door) > 0:
                        logger.info(f"if boss: {self.way_to_door=}")
                        self.go_while(self.way_to_door)

                    self.connect.get_html(URL_MAIN)
                    data = self.get_hp_mp()
                    self.restoring_hp(data, DUNGEON_HP_HEALING_BEFORE_BOSS)

                    # TODO
                    self.connect.get_html(URL_MAIN)
                    logger.info(f"{self.js_obj['a']=}")
                    data = self.get_hp_mp()
                    if MAG_KILLER:
                        healing_mp = DUNGEON_MP_HEALING_BEFORE_BOSS  # 0.4
                        need_mp = DUNGEON_MP_NEED_BEFORE_BOSS_FOR_MAG  # Turn  2_000
                    else:
                        healing_mp = DUNGEON_MP_HEALING_BEFORE_BOSS  # 0.4
                        need_mp = DUNGEON_MP_NEED_BEFORE_BOSS_FOR_WARRIOR  # 0
                    min_mp = data["my_max_mp"] * healing_mp  # 13100 * 0.4 = 5200
                    logger.error(f"min_mp {min_mp} , need_mp {need_mp}")
                    if min_mp < need_mp:
                        healing_mp = need_mp / data["my_max_mp"]
                        # # BUG DO NOT TOUCH THIS
                        # # healing_mp = (data["my_max_mp"] / need_mp) % 1  # (13100 / 6000) = 2.16 % 1 = 0.16
                        # # healing_mp = (need_mp / data["my_max_mp"]) % 1  # (13100 / 6000) = 2.16 % 1 = 0.16
                        if healing_mp > 1:
                            raise Exception(f"healing_mp > 1 {healing_mp=}")
                        logger.error(f"change percent from {DUNGEON_MP_HEALING_BEFORE_BOSS} to {healing_mp}")
                    self.restoring_mp(data, healing_mp)

                    self.connect.get_html(URL_MAIN)
                    self.get_status()
                    self.is_attack()
                    self.reward = True
                    # self.get_chat()
                else:
                    logger.info(f"self.floor < 3 {self.floor=} DONT GO TO BOSS")
            else:
                if self.doors or self.portal:
                    common_ways_list = []
                    if self.doors and not self.portal:
                        self.way_to_door = find_way_to_slave(self.js_obj, self.coord_doors)
                        self.check_right_way(self.way_to_door)
                    elif self.portal and not self.doors:
                        self.check_right_way(self.way_to_port)
                    else:
                        try:
                            self.way_to_door = find_way_to_slave(self.js_obj, self.coord_doors)
                        except KeyError:
                            logger.error(
                                "Cant find way. I think it's because we on port. "
                                "And we interrupt this iteration of the loop"
                            )
                            break
                        if len(self.way_to_door) > len(self.way_to_port):
                            for door_way in self.way_to_door:
                                for port_way in self.way_to_port:
                                    if door_way == port_way:
                                        common_ways_list.append(door_way)
                                        break
                        else:
                            for port_way in self.way_to_port:
                                for door_way in self.way_to_door:
                                    if door_way == port_way:
                                        common_ways_list.append(port_way)
                                        break
                        if common_ways_list:
                            self.go_while(common_ways_list)
                else:
                    logger.debug(f"\nWHEN WE DONT HAVE PORT AND DOOR {self.doors=} {self.portal=}\n")
                    not_visited = uncharted_path_slave(self.js_obj)
                    lists_ways = find_lists_ways_slave(self.js_obj, not_visited)
                    logger.debug(f"{not_visited=}")
                    logger.debug(f"{lists_ways=}")
                    if len(lists_ways) >= 1:
                        logger.debug(f"len(lists_ways) >= 1 ---- {len(lists_ways)=}")
                        my_set_difference = set(lists_ways[0])
                        logger.debug(f"{my_set_difference=}")
                        for ways in lists_ways[1:]:
                            my_set_difference.intersection_update(ways)
                        logger.debug(f"NEW {my_set_difference=}")
                        max_path_in_steps = max((way for way in lists_ways), key=len)
                        logger.debug(f"{max_path_in_steps=}")
                        right_way = []
                        for step in max_path_in_steps:
                            if step in my_set_difference:
                                my_set_difference.remove(step)
                                right_way.append(step)
                        logger.debug(f"{right_way=}")
                        if right_way:
                            logger.debug(f"go to right way")
                            self.go_while(right_way)
            # try:
            #     self.connect.get_html(URL_MAIN)
            #     self.get_status()
            #     self.string_info()
            #     self.my_coord = f"{self.js_obj['s']['x']}{self.js_obj['s']['y']}"
            # except KeyError:
            #     logger.info(f"Except KeyError self.js_obj['s']['x']self.js_obj['s']['y']/n {con.get_json()}")
            #     logger.info("maybe mobs on cell not yet killed")
            if self.reward and self.portal:
                ways_to_port = find_way_to_slave(self.js_obj, coord_port)
                if len(ways_to_port) > 0:
                    self.go_while(ways_to_port)
                self.connect.get_html(URL_MAIN)
                self.get_status()
                self.string_info()
                my_coord = f"{self.js_obj['s']['x']}{self.js_obj['s']['y']}"
                if (coord_port == my_coord) and self.reward:
                    logger.info(f"UP NEXT LEVEL {self.nickname} floor={self.floor}")
                    self.go_to_next_level()
                    next_level = True
            logger.debug(f"END while not next_level: sleep  {SLEEP_TIME}")
            logger.info(f"floor={self.floor} NEED WAIT because dont understand where going... floor={self.floor}")
            # # TODO floor
            # self.floor  = self.is_floor()
            time.sleep(float(SLEEP_TIME))
            # self.get_chat()
            self.connect.get_html(URL_MAIN)
            self.get_status()
            self.string_info()
        # TODO try it
        self.floor = self.is_floor()
        logger.info(f"\nfloor - '{self.floor}'")

    def _new_while(self) -> None:
        while True:
            self.check_key_new()
            self.check_doors()
            self.check_reward()
            logger.info(f"reward - {self.reward}")
            if not self.reward:
                if self.doors and self.key:
                    logger.info("KEY AND DOOR FIND GO TO REWARD!!!!!!!!!!!")
                    way_to = find_way_to(self.js_obj, self.coord_doors)
                    ways_to_door = create_right_way(self.js_obj, way_to)
                    if len(ways_to_door) < 5:
                        logger.info("need to go to door")
                        self.going_to_reward(ways_to_door)
                    else:
                        first_part = f"WAY TO DOOR TO LONG- {ways_to_door}"
                        second_part = f" type {type(ways_to_door)}"
                        text = first_part + second_part
                        logger.info(text)
            self.check_buttons()
            self.check_portal()
            logger.info(f"portal - {self.portal}")
            if (self.buttons and self.portal) and (self.doors and self.key):
                if not self.reward:
                    way_to = find_way_to(self.js_obj, self.coord_doors)
                    ways_to_door = create_right_way(self.js_obj, way_to)
                    logger.info("ALL DONE GO TO DOOR")
                    self.going_to_reward(ways_to_door)
                coord_port = self.get_coord_portal()
                my_coord = f"{self.js_obj['s']['x']}{self.js_obj['s']['y']}"
                if coord_port != my_coord:
                    go_to_port = find_way_to(self.js_obj, coord_port)
                    self.going_to(go_to_port)
                logger.info(f"UP NEXT LEVEL {self.nickname} floor={self.floor}")
                self.go_to_next_level()
                self.update_json()
                time.sleep(float(SLEEP_TIME))
                break
            ways = self.new_go()
            if ways:
                self.test_while(ways)

    def new_go(self) -> list:
        """
        Make first steps
        """
        not_visited = uncharted_path(self.js_obj)
        logger.info(f"----------- not_visited '{not_visited}'----------------")
        if not_visited:
            if PERSON_ROLE == SLAVE:
                go_to = find_near_way_slave(self.js_obj, not_visited)
            else:
                go_to = find_near_way(self.js_obj, not_visited)
            logger.info(f"----------- go_to '{go_to}'---- type '{type(go_to)}'")
            ways = create_right_way(self.js_obj, go_to)
        else:
            text = f"{NICKNAME} NO WAYS"
            logger.error(text)
            send_telegram(text)
            raise Exception(text)
        return ways

    def go_to_next_level(self) -> None:
        """
        Go to next level
        """
        if self.js_obj["a"].get("moveDeep"):
            vcode = self.js_obj["a"].get("moveDeep")
            data = {
                "type": "dungeon",
                "action": "moveDeep",
                "vcode": vcode,
                "r": random.random(),
            }
            self.connect.post_html(URL_EVENT, data)
            logger.info(
                f"---floor={self.floor}----{self.nickname}--NEXT LEVEL---{self.nickname}---floor={self.floor}----"
            )
            self.floor = self.is_floor()
        else:
            # # TODO: delete after test
            logger.debug(f"------{self.nickname}-can't activate portal----floor={self.floor}---\n")
            time.sleep(float(SLEEP_TIME))

    def _check_auto_buff(self) -> None:
        """check_auto_buff and use autobuff"""
        if AUTO_BUFF:
            text = "AUTO_BUFF ON"
            logger.critical(text)
            weapons = upivka.DICT_WEAPON.get(self.floor)
            text = f"{self.floor=} {weapons=}"
            logger.critical(text)
            if weapons and self.floor not in self.used_buff_floor:
                text = "USE AUTO_BUFF"
                logger.critical(text)
                self.used_buff_floor.append(self.floor)
                for weapon in weapons:
                    self.connect.get_html(URL_MAIN)

                    key = f"useWeapon.{weapon[1]}"
                    self.using_potion(weapon[0], key)

    def using_potion(self, count: int, key: str) -> None:
        """Use potion"""
        text = f"count {count}"
        logger.critical(text)
        self.get_status()
        for _ in range(int(count)):
            try:
                self.js_obj["a"][key]
            except Exception:
                text = f"{NICKNAME} ----NO POTION {key}!!!---"
                # logger.error(f"{self.js_obj=}")
                logger.error(text)
                send_telegram(text)
                # raise Exception(text)
                break
            item = key.replace("useWeapon.", "")
            vcode = self.js_obj["a"].get(key)
            data = {
                "type": "dungeon",
                "action": "useWeapon",
                "item": item,
                "vcode": vcode,
                "r": random.random(),
            }

            html = self.connect.post_html(URL_EVENT, data)

            logger.error(f"use weapon {key}")
            self.js_obj = json.loads(html.text)

    def parse_dungeon(self) -> dict:
        """
        Prepare 'data' for request
        """
        try:
            result = self.connect.get_result()
            if "text/html" in result.headers["Content-Type"]:
                result = self._find_pattern(FIND_VAR_OBJ_ACTION, result.text)
            else:
                send_text_message = f"Content-Type: {result.headers['Content-Type']}"
                logger.debug(f"{self.connect.get_result().headers['Content-Type']=}")
                logger.error(send_text_message)
                send_telegram(send_text_message)
                raise Exception(send_text_message)
            result = self._find_pattern(FIND_VAR_OBJ_ACTION)
            var_obj_actions = result.pop() + "}"
            actions = json.loads(var_obj_actions)
            query_data = {
                "type": "dungeon",
                "action": "getStatus",
                "vcode": actions.get("getStatus"),
                "r": random.random(),
            }
        except Exception:
            # # TODO: Написать обработку когда уже в бою!!!!!
            html = self.connect.get_html_page_text()
            send_text_message = f"{NICKNAME} ОТКЛЮЧИ КЛИЕНТ!!! ИЛИ ТЫ НЕ В ДАНЖЕ"
            if "var param_en" in html:
                logger.success(send_text_message)
                logger.success("RUN FIGHT")
                self.run_fight()
                logger.success("STOP FIGHT")

                logger.success("TRY AGAIN parse_dungeon")
                result = self._find_pattern(FIND_VAR_OBJ_ACTION)
                if result:
                    var_obj_actions = result.pop() + "}"
                    actions = json.loads(var_obj_actions)
                    query_data = {
                        "type": "dungeon",
                        "action": "getStatus",
                        "vcode": actions.get("getStatus"),
                        "r": random.random(),
                    }
                    logger.success("STOP TRY AGAIN parse_dungeon")
                else:
                    # # TODO: need check where am i
                    send_text_message = f"{NICKNAME} You not in dungeon"

            logger.error(send_text_message)
            send_telegram(send_text_message)
            raise Exception(send_text_message)
        return query_data

    # def parse_dungeon(self) -> dict:
    #     """
    #     Prepare 'data' for request
    #     """
    #     try:
    #         result = self._find_pattern(FIND_VAR_OBJ_ACTION)
    #         var_obj_actions = result.pop() + "}"
    #         actions = json.loads(var_obj_actions)
    #         query_data = {
    #             "type": "dungeon",
    #             "action": "getStatus",
    #             "vcode": actions.get("getStatus"),
    #         }
    #     except Exception:
    #         # # ! TODO: Написать обработку когда уже в бою!!!!!
    #         html = self.connect.get_html_page_text()
    #         send_text_message = f"{NICKNAME} ОТКЛЮЧИ КЛИЕНТ!!! ИЛИ ТЫ НЕ В ДАНЖЕ"
    #         if "var param_en" in html:
    #             logger.success(send_text_message)
    #             logger.success("RUN FIGHT")
    #             self.run_fight()
    #             logger.success("STOP FIGHT")
    #
    #             logger.success("TRY AGAIN parse_dungeon")
    #             result = self._find_pattern(FIND_VAR_OBJ_ACTION)
    #             if result:
    #                 var_obj_actions = result.pop() + "}"
    #                 actions = json.loads(var_obj_actions)
    #                 query_data = {
    #                     "type": "dungeon",
    #                     "action": "getStatus",
    #                     "vcode": actions.get("getStatus"),
    #                 }
    #                 logger.success("STOP TRY AGAIN parse_dungeon")
    #             else:
    #                 # # TODO: need check where am i
    #                 send_text_message = f"{NICKNAME} You not in dungeon"
    #
    #         logger.error(send_text_message)
    #         send_telegram(send_text_message)
    #         raise Exception("Fuck")
    #     return query_data

    def update_json(self) -> None:
        self.js_obj = self.connect.get_html_page_json()

    def get_status(self) -> None:
        """
        Get status. Need to take json answer

        To do that is self.connect.result must be text document!!!
        """
        data = self.parse_dungeon()
        html = self.connect.post_html(URL_EVENT, data)
        try:
            self.js_obj = json.loads(html.text)
        except Exception:
            text = f"{NICKNAME} Something wrong"
            logger.error(text)
            send_telegram(text)
            raise Exception(text)

    def start_party(self) -> None:
        """
        Looks like it is start dungeon
        """
        page = self.connect.get_html_page_text()
        try:
            self.js_obj = json.loads(page)
            actions = self.js_obj["a"]
        except json.decoder.JSONDecodeError:
            self.get_status()
            logger.info("USE WHEN ONLY START NEED")
            prepare = self._find_pattern(FIND_OBJ_ACTION)
            actions = json.loads(prepare[0])

        vcode = actions["startParty"]
        data = {
            "type": "dungeon",
            "action": "startParty",
            "vcode": vcode,
            "r": random.random(),
        }
        self.connect.post_html(URL_EVENT, data)
        self.connect.get_html_page_text()

    def create_party(self) -> None:
        """
        Looks like it is start dungeon
        """
        prepare = self._find_pattern(FIND_OBJ_ACTION)
        actions = json.loads(prepare[0])
        vcode = actions["createParty"]
        data = {
            "type": "dungeon",
            "action": "createParty",
            "vcode": vcode,
            "limit": 3,
            "r": random.random(),
        }
        self.connect.post_html(URL_EVENT, data)

    def get_info(self) -> str:
        """Get info about persons"""
        # TODO need use bytes LOGIN !!! NOT NICKNAME !!!
        site_url = URL_PLAYER_INFO + LOGIN
        self.connect.get_html(site_url)
        return self.connect.get_html_page_text()

    def get_fight_list(self) -> str:
        """Get info about persons"""
        site_url = URL + "/js/fight_v10.js"
        self.connect.get_html(site_url)

        result = self._find_pattern(FIND_POS_VARS)
        pos_vars_list = json.loads(result)

        result = self._find_pattern(FIND_POS_MANA)
        pos_mana_list = json.loads(result)

        result = self._find_pattern(FIND_POS_TYPE)
        pos_type_list = json.loads(result)

        result = self._find_pattern(FIND_POS_OCHD)
        pos_ochd_list = json.loads(result)

        return self.connect.get_html_page_text()

    def get_list_effects(self) -> list[str]:
        self.get_info()
        result: list[str] = self._find_pattern(FIND_VAR_EFF)
        if result:
            new_result = result.pop()
            new_result = new_result.replace("<b>", "").replace("</b>", "").replace("'", "")
            new_result = new_result.split("],[")
            new_result = list(map(lambda x: x.split(","), new_result))
        # TODO need typing
        return new_result

    def get_dict_effects(self) -> dict:
        list_effects = self.get_list_effects()
        new_dict = dict()
        for effect in list_effects:
            code_effect = effect[0]
            value = effect[1]
            part1, part2, part3 = value.split("(")

            effect_name = part1.strip()
            effect_count = part2.replace("x", "").replace(") ", "").strip()
            effect_remaining_time = part3.replace("еще", "").replace(")", "").strip()
            # TIME_FORMAT = "%H:%M:%S"
            # effect_remaining_time = datetime.strptime(effect_remaining_time, TIME_FORMAT)
            hours, minutes, seconds = effect_remaining_time.split(":")
            now = datetime.now()
            effect_timedelta = timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
            effect_timedelta_timestamp = timedelta(
                hours=int(hours), minutes=int(minutes), seconds=int(seconds)
            ).total_seconds()
            effect_end_time = now + effect_timedelta
            effect_string = f"{effect_name} {effect_count} {effect_remaining_time}"
            logger.debug(effect_string)

            new_dict[code_effect] = {
                "effect_name": effect_name,
                "effect_count": int(effect_count),
                "effect_remaining_time": effect_remaining_time,
                "effect_string": effect_string,
                "effect_timedelta": effect_timedelta,
                "effect_end_time": effect_end_time,
                "effect_timedelta_timestamp": effect_timedelta_timestamp,
            }
        return new_dict

    def get_effects_from_info(self) -> list[str]:
        self.get_info()
        result = self._find_pattern(FIND_VAR_EFF)
        if result:
            new_result = result.pop()
            new_result = new_result.replace("<b>", "").replace("</b>", "").replace("'", "")
            new_result = new_result.split("],[")
            new_result = list(map(lambda x: x.split(","), new_result))
        return new_result

    def get_chat(self) -> None:
        url = URL_KEEP_CONNECTION.format(rand_float=random.random())
        self.connect.get_html(url)
        text_string = self.connect.get_html_page_text()
        self.connect.get_html(URL_MAIN)
        pattern = r"(?<=\.add_msg\().+(?=\);)"
        finder = re.compile(pattern)
        messages = finder.findall(text_string)
        logger.info(f"get_chat {messages=}")
        self.is_message_for_person(messages)

    @staticmethod
    def is_message_for_person(messages: list[str]):
        pattern = r"(?<=<SPL>).+(?=<SPL>)"
        finder = re.compile(pattern)
        for mes in messages:
            text = finder.findall(mes)
            if text:
                if NICKNAME in str(text[0]):
                    from_name = r"(?<=<SPAN>).+(?=</SPAN>)"
                    finder2 = re.compile(from_name)
                    sender_name = finder2.findall(str(text[0]))
                    if sender_name:
                        only_text_pattern = r"(?<=<font color=.{7}).+(?=</font>)"
                        finder3 = re.compile(only_text_pattern)
                        only_text = finder3.findall(mes)
                        text_for_message = (
                            f"Игроку {NICKNAME} пишут в чат!\nОтправитель: {sender_name[0]} --- {only_text[0]}"
                        )
                        logger.error(text_for_message)
                        send_telegram(text_for_message)

    def ab_while(self) -> None:
        while True:
            # put_on_a_belt_class(self.connect)  # put mana on belt
            # heal_after_fight_class(self.connect)  # heal hp\mp
            self.check_frame()
            # self.check_fight()

            # run_fight(connect, False)  # One hit
            # self.run_fight()  # FULL fight
            self.switch_to_inventory()
            time_sleep = random.uniform(10, 20)
            logger.error(f"ab_while time.sleep({time_sleep})")
            time.sleep(time_sleep)
            self.get_chat()

            # # TODO: поправить
            # test
            # put_on_a_belt_class(self.connect)  # put mana on belt

            # heal_after_fight_class(self.connect)  # heal hp\mp

    def check_frame(self):
        """NOT USED YET
        this code check frame check effect and use potion
        """
        self.num_iter = 0
        frame = True
        while frame:
            # self.connect.get_html(URL_MAIN)
            self.num_iter += 1
            logger.error(f"{self.num_iter=}")
            result = self._find_pattern(FIND_FRAME)
            logger.error(f"frame {result=}")
            if result:
                if (self.num_iter % 1) == 0:
                    self.num_iter = 1
                    # self.connect.get_html(config.URL_MAIN + "?wca=27")
                    # self.effects.update_page_text(self.connect.get_result())
                    # self.effects.set_update_use_time()

                    # self.switch_to_inventory()
                    # # TODO: исправить
                    # self.use_potions()
                    # self.update_all_data()
                # time_sleep = 30

                # self.connect.get_html(URL_MAIN)
                time_sleep = random.uniform(10, 15)
                logger.error(f"check_frame time.sleep({time_sleep})")
                time.sleep(time_sleep)
                # Не понятно зачем. надо тестить
            else:
                # # OLDEST THINGS
                while True:
                    # error = re.findall(r"error.css", html.text)
                    pattern = r"error.css"
                    error = self._find_pattern(pattern)
                    if error:
                        logger.trace("NEED RELOGIN!!!")
                        logger.trace("NEED RELOGIN!!!")
                        logger.trace("NEED RELOGIN!!!")
                        self.init_connection()
                        self.switch_to_inventory()
                        break
                    # logger.debug(f"{self.connect.get_html_page_text()=}")
                    self.switch_to_inventory()
                    self.connect.get_html(URL_MAIN)
                    time_sleep = random.uniform(10, 15)
                    logger.error(f"while True: check_frame time.sleep({time_sleep})")
                    time.sleep(time_sleep)
                    break
                self.switch_to_inventory()
                frame = False
                logger.error("not frame")
                time_sleep = random.uniform(10, 15)
                logger.error(f"else check_frame time.sleep({time_sleep})")
                time.sleep(time_sleep)
                # self.connect.get_html(URL_MAIN)
            # self.connect.get_html(URL_MAIN)
            self.get_chat()

    def siege(self):
        self.siege_while()
        self.run_fight()
        logger.debug("END!")

    def siege_while(self) -> bool:
        num_iter = 0
        while True:
            num_iter += 1
            frame = self._find_pattern(FIND_FRAME)
            logger.error(f"frame {frame}")
            if frame:
                if (num_iter % 50) == 0:
                    logger.error(f"num_iter % 50 {num_iter}")
                    num_iter = 1
                time.sleep(0.1)
                self.connect.get_html(URL_MAIN)
            else:
                while True:
                    num_iter += 1
                    pattern = r"error.css"
                    error = self._find_pattern(pattern)
                    if error:
                        self.init_connection()
                        break
                    pattern = r"(?<=fight_pm = \[).+(?=];)"
                    fight = self._find_pattern(pattern)
                    if not fight:
                        if (num_iter % 500) == 0:
                            logger.error(f"num_iter % 50 {num_iter}")
                            num_iter = 1
                        time.sleep(0.1)
                        self.connect.get_html(URL_MAIN)
                    else:
                        return True
            # self.get_chat()
            # time.sleep(0.1)

    def where_i_am(self) -> Location:
        """where i am"""
        """
        При входе может находится перс на 3х этапах
        1 - инфо
        2 - инвентарь
        3 - природа ну или город
        """
        html = self.connect.get_html_page_text()

        # # Just test!!!!  WORK!!!!
        # person_info = self.get_info()
        # self.parameters.update_params(person_info)
        # parameter = self.parameters.parse()
        # logger.success(f"{parameter=}")

        # self.connect.make_file(html, "first_check")
        if "var param_en" in html:
            logger.success("in fight")
            # location = "fight"
            return Location.FIGHT

        if "DISABLED" not in html:
            logger.success("on nature")
            # location = "nature"
            self.prepare = list()
            return Location.NATURE

        if '"Инвентарь" DISABLED>' in html:
            # # TODO: refactoring
            """ELIXIR have the same as invetar but not"""
            logger.success("in inventar")
            # self.connect.make_file(html, "Not_inventar")
            # location = "inventar"
            self.prepare = list()
            return Location.INVENTAR

        # pattern = r"(?<=Инвентарь\" onclick=\"location=\'main\.php\?).+(?=\'\">)"  # in city
        # pattern = r'(?<=&go=inv&vcode=).+(?=\'\" value=\"Инвентарь)'  # mb oktal
        # pattern = FIND_IN_CITY
        # prepare = re.findall(pattern, html)
        prepare = self._find_pattern(FIND_IN_CITY, html)
        logger.debug(f"{prepare=}")
        if prepare:
            logger.success("in city")
            self.prepare = prepare
            return Location.CITY

        # pattern = r"(?<=&go=inv&vcode=).+(?=\'\" value=\"Инвентарь)"
        # pattern = FIND_PAGE_INVENTAR
        # prepare = re.findall(pattern, html)
        prepare = self._find_pattern(FIND_PAGE_INVENTAR, html)
        if not prepare:
            logger.success("in elixir")
            return Location.ELIXIR

        self.prepare = prepare
        logger.success("in info")
        return Location.INFO

    def get_dressed(self, kit_name) -> None:
        """get_dressed kit_name"""
        # logger.critical(f"get_result = {self.connect.get_html_page_text()}")
        # pattern = r'(?<=ГОС\",\").+(?=\"\);)'
        part1 = r"(?<="
        part2 = r"\",\").+(?=\"\);)"
        pattern = part1 + kit_name + part2
        # prepare = re.findall(pattern, self.connect.get_html_page_text())
        prepare = self._find_pattern(pattern)
        logger.critical(f"{prepare=}")
        # test = prepare[0].replace('"', "").split(",")
        uid, vcode = prepare[0].replace('"', "").split(",")
        # logger.critical(f"{test=}")
        data = {"get_id": "57", "s": "2", "uid": uid, "vcode": vcode}
        self.connect.get_html(URL_MAIN, data=data)
        # logger.critical(self.connect.get_html(config.URL_MAIN, data=data))

    def put_on_scroll(self) -> None:
        """
        put_on_scroll
        dont matter use count
        """
        site_url = "http://www.neverlands.ru/main.php?wca=28"
        self.connect.get_html(site_url)
        # pattern = r"(?<=http://image\.neverlands\.ru/weapon/w28_167\.gif).+?\">"  # w28_167 - имп вред
        # pattern = FIND_IMP_PAST

        # pattern = r"(?<=http://image\.neverlands\.ru/weapon/i_svi_212\.gif).+?\">"  # i_svi_212 - удар ярости
        # pattern = FIND_SCROLL_STRIKE_FURY
        # prepare = re.findall(pattern, self.connect.get_html_page_text())
        prepare = self._find_pattern(FIND_SCROLL_STRIKE_FURY)
        # logger.critical(self.connect.get_html_page_text())
        if not prepare:
            text = "No scrolls----"
            logger.critical(text)
            raise Exception(text)
        # pattern2 = r"(?<=php\?).+(?='\")"  # паттерн на строку с запросом
        # pattern2 = FIND_STRING_WITH_QUERY
        # # (?<=Долговечность: <b>)\d+/\d+(?=</b>)  # паттерн на долговечку
        # prepare2 = re.findall(pattern2, prepare[0])
        prepare2 = self._find_pattern(FIND_STRING_WITH_QUERY, prepare[0])
        if not prepare2:
            text = f"{NICKNAME} DONT UNDERSTAND WHY"
            logger.critical(text)
            send_telegram(text)
            raise Exception(text)
        data = {}
        my_iter = prepare2[0].split("&")
        list_of_dict = list(map(lambda x: {x.split("=")[0]: x.split("=")[1]}, my_iter))
        for item in list_of_dict:
            data.update(item)

        logger.critical(f"request : {data}")
        self.connect.get_html(URL_MAIN, data=data)

    def from_city_to_inventar(self) -> None:
        """construct the request and send it"""
        logger.success("in city")
        prepare = self._find_pattern(FIND_IN_CITY)
        vcode = prepare[0].split("=")[-1]
        data = {"get_id": "56", "act": "10", "go": "inv", "vcode": vcode}
        self.connect.get_html(URL_MAIN, data=data)

    def from_nature_to_inventar(self) -> None:
        """construct the request and send it"""
        logger.success("in nature")
        prepare = self._find_pattern(FIND_FROM_NATURE_TO_INV)
        logger.debug(f"{prepare=}")
        if prepare:
            request_data = {"get_id": "56", "act": "10", "go": "inv", "vcode": prepare[0]}
            self.connect.get_html(URL_MAIN, data=request_data)

    def from_info_to_inventar(self) -> None:
        """construct the request and send it"""
        logger.success("in info")
        if not self.prepare:
            logger.debug("not self.prepare")
            prepare = self._find_pattern(FIND_PAGE_INVENTAR)
        else:
            logger.debug("self.prepare exists")
            prepare = self.prepare
        if prepare:
            vcode = prepare[0].split("=")[-1]
            data = {"get_id": "56", "act": "10", "go": "inv", "vcode": vcode}
            self.connect.get_html(URL_MAIN, data=data)
        else:
            logger.debug('from_info_to_inventar not find ?<=&go=inv&vcode=).+(?=\'" value="Инвентарь')

    def from_elixir_to_inventar(self, html):
        """construct the request and send it"""
        logger.success("in elixir")
        site_url = "http://www.neverlands.ru/main.php?wca=28"
        self.connect.get_html(site_url)

    def do_nothing(self) -> None:
        """Do nothing"""
        pass

    def switch_to_inventory(self) -> None:
        """Switch to inventory or fight and switch"""
        logger.info("def switch_to_inventory")
        self.connect.get_html(URL_MAIN)
        location = self.where_i_am()
        logger.success(f"{location.value=}")

        location_to_inventory = {
            Location.FIGHT.value: self.run_fight,
            Location.CITY.value: self.from_city_to_inventar,
            Location.NATURE.value: self.from_nature_to_inventar,
            Location.INVENTAR.value: self.do_nothing,
            Location.ELIXIR.value: self.from_elixir_to_inventar,
            Location.INFO.value: self.from_info_to_inventar,
        }
        location_to_inventory[location.value]()

        # # TODO: NEED REFACTOR!!!!!
        # self.get_dressed(SIEGE_DRESS)  # ГОС

        # self.put_on_scroll()

        # self.find_teleport(scroll.Teleport(TELEPORT_CITY))  # Teleport.FP OKTAL
        # self.find_teleport(Teleport(TELEPORT_CITY))  # Teleport.FP OKTAL
        # # AFTER REFACTORING. NEED TEST
        # self.find_teleport(Teleport(TELEPORT_CITY))  # TELEPORT_CITY = 2 - Teleport.FP OKTAL

        # self.enter_the_tower(CITY)  #

        # self.add_to_siege()

    # # TODO: NEED REFACTOR!!!!!
    def find_teleport(self, city: Teleport) -> None:
        """Check teleport and use it to TP"""
        # # TODO: NEED REFACTOR!!!!!
        site_url = "http://www.neverlands.ru/main.php?wca=28"
        self.connect.get_html(site_url)
        # pattern = r"(?<=http://image\.neverlands\.ru/weapon/w28_167\.gif).+?\">"  # w28_167 - имп вред
        # pattern = FIND_IMP_PAST
        # pattern = r"(?<=http://image\.neverlands\.ru/weapon/i_w28_22\.gif).+?\">"  # i_w28_22 - телепорт
        # pattern = FIND_TELEPORT
        # prepare = re.findall(pattern, self.connect.get_result())
        prepare = self._find_pattern(FIND_TELEPORT)
        if not prepare:
            text = f"{NICKNAME} No scrolls Teleport----"
            logger.error(text)
            send_telegram(text)
            raise Exception(text)
        # pattern2 = r"(?<=w28_form\(').+(?='\)\")"  # паттерн на строку с запросом точно хотите юзать
        # (?<=Долговечность: <b>)\d+/\d+(?=</b>)  # паттерн на долговечку
        # pattern2 = FIND_USE
        # prepare2 = re.findall(pattern2, prepare[0])
        prepare2 = self._find_pattern(FIND_USE, prepare[0])
        if not prepare2:
            logger.error(f"{prepare[0]=}")
            text = f"{NICKNAME} DONT UNDERSTAND WHY"
            logger.error(text)
            send_telegram(text)
            # raise Exception(text)
        data = {
            "post_id": "25",
            "agree": AGREE,
            # 'wtelid': scroll.TELEPORT.get(city)
            "wtelid": city.value,
        }
        clean_data = prepare2[0].replace("'", "").split(",")
        data["vcode"] = clean_data[0]
        data["wuid"] = clean_data[1]
        data["wsubid"] = clean_data[2]
        data["wsolid"] = clean_data[3]

        logger.debug(f"request : {data}")
        self.connect.post_html(URL_MAIN, data)


class Parameters:
    def __init__(self) -> None:
        self.text: str

    def update_params(self, text: str) -> None:
        """Take page info"""
        self.text = text

    def parse(self):
        """Prepare parameters

        Not it works only TuRnOff
        """
        prepare = re.findall(FIND_STATS, self.text)
        prepared = prepare[0].split("],[")
        params = (
            "Сила",
            "Ловкость",
            "Удача",
            "Знания",
            "Здоровье",
            "Мудрость",
            "Класс брони",
            "Уловка",
            "Точность",
            "Сокрушение",
            "Стойкость",
            "Пробой брони",
        )
        param_dict = dict.fromkeys(params)
        for num, key in enumerate(param_dict.keys()):
            param_dict[key] = prepared[num].replace("[", "").replace("]", "").replace(f"'{key}',", "").split(",")
        return param_dict
