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


HEAL = "101"  # "элексир восстановления"

PLANAR = "152"  # планар

BAIT = "102"  # Приманку Для Ботов


# def my_timer():
#     def decorator(function):
#         def wrapper(*args, **kwargs):
#             logger.debug(f"{function.__name__=}")
#             start_time = time.perf_counter()
#             result = function(*args, **kwargs)
#             logger.debug(f"iter_time - {time.perf_counter() - start_time}")
#             return result

#         return wrapper

#     return decorator


def timing_decorator(func):
    def wrapper(*args, **kwargs):
        logger.critical(f"{func.__name__=}")
        logger.debug(f"{kwargs=}")
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        logger.critical(f"timing_decorator {func.__name__=} - {end_time - start_time:.5f} seconds")
        return result

    return wrapper


class Game:
    def __init__(self) -> None:
        self.iter_number: int = 0

        self.my_hp = 10_000

        self.my_mp = 7_000

        self.fight_planar: bool = False

        self.fight_bait: bool = False

        self.init_connection()

        self.fight_class: Fight = Fight()

        self.full_fight: bool = True
        logger.success("__init__")

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

        self.fight_class.fight()
        data = self.fight_class.get_queries_param()
        inu = data.inu
        inb = data.inb
        ina = data.ina

        part1 = f"inu-{inu} inb-{inb} ina-{ina}"
        part2 = f" my_od-{my_od} my_mp-{my_mp}"
        part3 = f" my_hp-{my_hp}"
        self.my_hp = my_hp
        self.my_mp = my_mp
        text = part1 + part2 + part3
        logger.debug(text)
        return self.fight_class.get_data()

    def parse_fight(self, fight_iteration: int) -> dict[str, str]:
        """Parse FIGHT"""
        self.check_live()
        data = self.check_end_battle()  # check and if True create data
        if data:
            return data

        self.fight_class.setup_value(self.connect.get_html_page_text(), fight_iteration)

        data = self.logic()
        return data

    def stop_or_hit(self, fight_iteration: int) -> None:
        data = self.parse_fight(fight_iteration)
        if "post_id" in data.keys():
            # TODO do hit!
            self.connect.post_html(URL_MAIN, data)
            self.continue_fight = True
        else:
            # This is and of battle
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

    @timing_decorator
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

        logger.success(f"{self.full_fight=}")
        self.continue_fight = self.full_fight
        while self.continue_fight:
            self.check_not_error()
            self.stop_or_hit(fight_iteration)
            fight_iteration += 1
            start_time = check_iter(fight_iteration, start_time)

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

    def to_elixir(self):
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
        self.go_to_elixir()

    def bait(self) -> str:

        self.to_elixir()

        self.ab_while()

        text = f"{NICKNAME} All Done"
        send_telegram(text)
        return text

    def ab_while(self) -> None:
        # TODO 4800 --- bait планар   4200 приманки минимум. но лучше 8400
        # 1) вхожу
        # 2) просто инвентарь http://neverlands.ru/main.php?im=0
        # 3) захожу в инвентарь элексиры  http://neverlands.ru/main.php?im=6
        # 4) запускается цикл
        #   4.1) лечение  101
        #   4.2) юзаем планар. если вернулся пустой ответ юзаем приманку
        #   4.3) бой
        #   4.4) каждый 100 бой
        #    4.5) запрос на получание чата чтобы не релогиниться
        #    4.6) опять запрос на инвентарь просто инвентарь http://neverlands.ru/main.php?im=0
        #    4.7) захожу в инвентарь элексиры  http://neverlands.ru/main.php?im=6
        #   4.4)
        #   4.4)
        #   4.4)
        #   4.4)
        #   "элексир восстановления"
        #   http://neverlands.ru/main.php?get_id=43&act=101&uid=203429153&curs=20&subid=0&ft=0&vcode=ecaab696d733cc9c21a48cf1afcf2ddc
        #   curs = количество юзов в банке
        # act=101 "элексир восстановления"
        # act=102 Приманку Для Ботов
        # act=103 Бутылку Шампанского
        # act=104 Эликсир Мгновенного Исцеления
        # act=105 Зелье Кровожадности
        # act=106 Эликсир Быстроты
        # act=107 Эликсир Блаженства
        # act=108 Дар Иланы
        # act=109 Эликсир из Подснежника
        # act=110 Молодильное яблочко
        # act=156 Фаросское Вино
        # act=152 Приманку Для Ботов  ---- Планар!!!
        # act=161 Усиление огня
        #   приманку
        # http://neverlands.ru/main.php?get_id=43&act=102&uid=201875330&curs=89&subid=0&ft=0&vcode=ddc527cef1063c007174fa049bd1df51
        # http://neverlands.ru/main.php?get_id=43&act=102&uid=201875330&curs=89&subid=0&ft=0&vcode=272d6037e6d9bcbc2a4fad1dbb88a2c8
        # просто инвентарь http://neverlands.ru/main.php?im=0
        while True:
            # HACK
            if self.iter_number == 30:
                break
            logger.warning(f"{self.iter_number=}")
            self.to_elixir()

            if self.my_hp < 7_000 or self.my_mp < 5_000:
                self.use(item=HEAL)

            self.use(item=PLANAR)
            # self.use(item=BAIT)

            res = self.connect.get_html_page_text()
            # logger.success(f"{res=}")
            if "var param_en" in res:
                logger.success("IN fight planar")
                self.run_fight()
                self.fight_planar = True
            # else:
            #     self.fight_planar = False
            #     self.use(item=BAIT)
            #     res2 = self.connect.get_html_page_text()
            #     # logger.success(f"{res2=}")
            #     if "var param_en" in res2:
            #         logger.success("IN fight bait")
            #         self.run_fight()
            #         self.fight_bait = True
            #     else:
            #         self.fight_bait = False

            # if not self.fight_planar and not self.fight_bait:
            #     time.sleep(1)

            # if self.iter_number % 100 == 0:
            #     self.get_chat()
            #     self.go_to_inventory()

            self.iter_number += 1

    def go_to_inventory(self) -> None:
        logger.success("go_to_inventory")
        data = {"im": 0}
        self.connect.get_html(URL_MAIN, data=data)

    def go_to_elixir(self) -> None:
        logger.success("go_to_elixir")
        data = {"im": 6}
        self.connect.get_html(URL_MAIN, data=data)

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

    @timing_decorator
    def use(self, *, item: str) -> None:
        """Heal HP\MP"""
        first_part = r"(?<=get_id=43&act="
        second_part = "&uid=).+?' }"
        pattern = first_part + item + second_part
        results = self._find_pattern(pattern)
        for string in results:
            arg_lst = string.replace(r"' }", "").split("&")

        try:
            data = {
                "get_id": 43,
                "act": item,
                "uid": arg_lst[0],
            }
        except UnboundLocalError:
            logger.error(f"{results=}")
            logger.error(f"{pattern=}")
            logger.error(f"{item=}")
            # logger.error(f"{self.connect.get_html_page_text()=}")

        for item in arg_lst[1:]:
            key, value = item.split("=")
            data[key] = value

        self.connect.get_html(URL_MAIN, data=data)

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
