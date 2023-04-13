import random
import re
import time

from loguru import logger

from config.pattern import FIND_IN_CITY
from config.pattern import FIND_FEXP
from config.pattern import FIND_PARAM_OW
from config.pattern import FIND_PAGE_INVENTORY
from config.pattern import FIND_FROM_NATURE_TO_INV

from config.urls import URL_MAIN
from config.urls import URL_KEEP_CONNECTION

from config.local_config import NICKNAME
from config.local_config import PROXY
from config.local_config import PROXIES
from config.local_config import PROXY_IP

from fight import Fight

from request import Connection
from request import send_telegram

from location.classes import Location


HEAL = "101"  # "элексир восстановления"

PLANAR = "152"  # планар

BAIT = "102"  # Приманку Для Ботов


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


def check_iter(fight_iteration: int, start_time: float) -> float:
    """Count iteration and time

    :param fight_iteration: Count iteration
    :type fight_iteration: int
    :param start_time: time start
    :type start_time: float
    :return: time end
    :rtype: float
    """
    logger.info(f"fight_iteration - '{fight_iteration}'")
    if fight_iteration % 50 == 0:
        text = f"{NICKNAME} ----TOO LONG FIGHT---- >= {fight_iteration}"
        logger.error(text)
        send_telegram(text)
    end_time = time.perf_counter()
    logger.debug(f"iter_time - {end_time - start_time}")
    return end_time


class Game:
    def __init__(self, fight: Fight, connect: Connection) -> None:
        self.fight_class = fight
        self.connect = connect

        self._init_variables()

        logger.success("__init__")

    def _init_variables(self) -> None:
        """Init variables"""
        self.iter_number: int = 0
        self.my_hp: int = 5_000
        self.my_mp: int = 5_000
        self.fight_planar: bool = False
        self.fight_bait: bool = False
        self.nickname: str = NICKNAME
        self.end_battle: list[str | None] = list()

    def _find_pattern(self, pattern: str, search_string: str = None) -> list[str | None]:
        """Find from pattern

        :param pattern: pattern
        :type pattern: str
        :param search_string: search string, defaults to None
        :type search_string: str, optional
        :return: result
        :rtype: list[str | None]
        """
        if search_string:
            return re.findall(pattern, search_string)
        return re.findall(pattern, self.connect.get_html_page_text())

    def _is_alive(self) -> None:
        """Check live status in battle"""
        result = self._find_pattern(FIND_PARAM_OW)
        if result:
            self._raise_error(result)

    def _raise_error(self, result: list[str]) -> None:
        """Raise dead in battle

        :param result: list with params in one string
        :type result: list[str]
        :raises Exception: Trouble need check logs
        """
        new_result = result.pop()
        param_ow = new_result.replace("]", "").replace('"', "").replace("[", "").split(",")
        if param_ow[1] == "0":
            text_for_message = f"{NICKNAME} YOU KILLED BUT FIGHT NOT ENDED"
            logger.error(text_for_message)
            send_telegram(text_for_message)
            raise Exception(text_for_message)

    def _prepare_data_end_battle(self, fexp: list[str]) -> dict[str, str]:
        """Prepare data to end battle in battle

        :param fexp: values
        :type fexp: list[str]
        :return: query data
        :rtype: dict[str, str]
        """
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

    def _is_end_battle(self) -> bool:
        """Check end battle in battle

        :return: is end battle
        :rtype: bool
        """
        self.end_battle = self._find_pattern(FIND_FEXP)
        if self.end_battle:
            return True
        return False

    def _create_end_battle_data(self) -> dict[str, str]:
        """Create end battle data

        :return: query data
        :rtype: dict[str, str]
        """
        new_result: str = self.end_battle.pop()
        fexp: list[str] = new_result.replace("]", "").replace('"', "").replace("[", "").split(",")
        return self._prepare_data_end_battle(fexp)

    def _logic(self) -> dict[str, str]:
        """Get HP/MP create query data

        :return: query data
        :rtype: dict[str, str]
        """
        my_od, my_mp, my_hp = self.fight_class.get_state()
        self.my_hp = my_hp
        self.my_mp = my_mp

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

    def _parse_fight(self, fight_iteration: int) -> dict[str, str]:
        """Parse FIGHT

        :param fight_iteration: number of moves
        :type fight_iteration: int
        :return: data to request
        :rtype: dict[str, str]
        """
        self._is_alive()
        if self._is_end_battle():
            data = self._create_end_battle_data()

        self.fight_class.setup_value(self.connect.get_html_page_text(), fight_iteration)

        data = self._logic()
        return data

    def _stop_or_hit(self, fight_iteration: int) -> None:
        """Check stop battle

        :param fight_iteration: number of moves
        :type fight_iteration: int
        """
        data = self._parse_fight(fight_iteration)
        if "post_id" in data.keys():
            # This is hit!
            self.connect.post_html(URL_MAIN, data)
            self.continue_fight = True
        elif "retry" in data.keys():
            logger.debug("retry")
            self.connect.get_html(URL_MAIN)
            self.continue_fight = True
        else:
            # This is end of battle
            logger.info("Get a request for the end battle")
            self.connect.get_html(URL_MAIN, data)
            self.continue_fight = False

    def _is_error(self) -> bool:
        """Check error

        :return: is error
        :rtype: bool
        """
        pattern = r"error.css"
        error = self._find_pattern(pattern)
        if error:
            return True
        return False

    def _reconnect(self) -> None:
        """Relogin"""
        logger.trace("\nNEED RELOGIN!!!")
        logger.trace("DO RELOGIN!!!\n")
        self.connect.reconnect()

    @timing_decorator
    def run_fight(self) -> None:
        """Fight while"""
        fight_iteration = 0
        start_time = time.perf_counter()

        self.continue_fight = True
        while self.continue_fight:
            if self._is_error():
                self._reconnect()
            self._stop_or_hit(fight_iteration)
            fight_iteration += 1
            start_time = check_iter(fight_iteration, start_time)

    def _from_city_to_inventory(self) -> None:
        """construct the request and send it"""
        logger.success("in city")
        prepare = self._find_pattern(FIND_IN_CITY)
        vcode = prepare[0].split("=")[-1]
        data = {"get_id": "56", "act": "10", "go": "inv", "vcode": vcode}
        self.connect.get_html(URL_MAIN, data=data)

    def from_nature_to_inventory(self) -> None:
        """construct the request and send it"""
        logger.success("in nature")
        prepare = self._find_pattern(FIND_FROM_NATURE_TO_INV)
        logger.debug(f"{prepare=}")
        if prepare:
            request_data = {"get_id": "56", "act": "10", "go": "inv", "vcode": prepare[0]}
            self.connect.get_html(URL_MAIN, data=request_data)

    def from_info_to_inventory(self) -> None:
        """construct the request and send it"""
        logger.success("in info")
        if not self.prepare:
            logger.debug("not self.prepare")
            prepare = self._find_pattern(FIND_PAGE_INVENTORY)
        else:
            logger.debug("self.prepare exists")
            prepare = self.prepare
        if prepare:
            vcode = prepare[0].split("=")[-1]
            data = {"get_id": "56", "act": "10", "go": "inv", "vcode": vcode}
            self.connect.get_html(URL_MAIN, data=data)
        else:
            logger.debug('from_info_to_inventory not find ?<=&go=inv&vcode=).+(?=\'" value="Инвентарь')

    def from_elixir_to_inventory(self, html):
        """construct the request and send it"""
        logger.success("in elixir")
        site_url = "http://www.neverlands.ru/main.php?wca=28"
        self.connect.get_html(site_url)

    def do_nothing(self) -> None:
        """Do nothing"""
        pass

    def to_elixir(self) -> None:
        """construct the request and send it"""
        location = self.where_i_am()
        logger.success(f"{location.value=}")

        location_to_inventory = {
            Location.FIGHT.value: self.run_fight,
            Location.CITY.value: self._from_city_to_inventory,
            Location.NATURE.value: self.from_nature_to_inventory,
            Location.INVENTORY.value: self.do_nothing,
            Location.ELIXIR.value: self.from_elixir_to_inventory,
            Location.INFO.value: self.from_info_to_inventory,
        }
        location_to_inventory[location.value]()
        self.go_to_elixir()

    def bait(self) -> str:
        """Start bait

        :return: result
        :rtype: str
        """

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
        # When you are login person can be in these three position
        # 1 - info
        # 2 - inventory
        # 3 - city or nature
        html = self.connect.get_html_page_text()

        if "var param_en" in html:
            logger.success("in fight")
            return Location.FIGHT

        if "DISABLED" not in html:
            logger.success("on nature")
            self.prepare = list()
            return Location.NATURE

        if '"Инвентарь" DISABLED>' in html:
            # HACK ELIXIR have the same as inventory but not
            logger.success("in inventory")
            self.prepare = list()
            return Location.INVENTORY

        prepare = self._find_pattern(FIND_IN_CITY, html)
        logger.debug(f"{prepare=}")
        if prepare:
            logger.success("in city")
            self.prepare = prepare
            return Location.CITY

        prepare = self._find_pattern(FIND_PAGE_INVENTORY, html)
        if not prepare:
            logger.success("in elixir")
            return Location.ELIXIR

        self.prepare = prepare
        logger.success("in info")
        return Location.INFO
