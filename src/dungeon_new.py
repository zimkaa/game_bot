import re
import time

from loguru import logger

from config import COUNT_ITER  # noqa: I100
from config import FIND_ERROR
from config import FIND_FEXP
from config import FIND_FIGHT
from config import FIND_PARAM_OW
from config import FIND_USE_ITEM_PART1
from config import FIND_USE_ITEM_PART2
from config import NICKNAME
from config import START_HP
from config import START_ITER
from config import START_MP
from config import URL_MAIN

from elixir import Elixir

from enemy import Summon
from enemy import SummonBotType

from fight import Fight

from helpers import timing_decorator

from person_chat import PersonChat

from person_location import Location
from person_location import PersonLocation

from request import Connection
from request import send_telegram


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
    def __init__(
        self,
        *,
        fight: Fight,
        connect: Connection,
        person_location: PersonLocation,
        person_chat: PersonChat,
        nickname: str,
    ) -> None:
        self._fight_class = fight
        self._connect = connect
        self._person_location = person_location
        self._person_chat = person_chat
        self._nickname = nickname

        self._init_variables()

        logger.success("__init__")

    def _init_variables(self) -> None:
        """Init variables"""
        self._iter_number: int = START_ITER
        self._my_hp: int = START_HP
        self._my_mp: int = START_MP
        self._my_od: int = 0
        self._inu: str = ""
        self._inb: str = ""
        self._ina: str = ""
        self._continue_fight: bool = False
        self._end_battle: list[str] = list()

    def _check_alive(self) -> None:
        """Check live status in battle"""
        result: list[str] = re.findall(FIND_PARAM_OW, self._connect.get_html_page_text())
        if result:
            new_result = result.pop()
            param_ow = new_result.replace("]", "").replace('"', "").replace("[", "").split(",")
            if param_ow:
                hp = param_ow[1]
                if not self._is_alive(hp):
                    self._raise_error()

    def _is_alive(self, hp: str) -> bool:
        """is alive

        :param hp: my hp
        :type param_ow: str
        :return: true or false
        :rtype: bool
        """
        if hp == "0":
            return False
        return True

    def _raise_error(self) -> None:
        """Raise dead in battle

        :raises Exception: Trouble need check logs
        """
        text_for_message = f"{self._nickname} YOU KILLED BUT FIGHT NOT ENDED"
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
        text_for_message = f"{self._nickname} END BATTLE"
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
        self._end_battle = re.findall(FIND_FEXP, self._connect.get_html_page_text())
        if self._end_battle:
            return True
        return False

    def _create_end_battle_data(self) -> dict[str, str]:
        """Create end battle data

        :return: query data
        :rtype: dict[str, str]
        """
        new_result: str = self._end_battle.pop()
        fexp: list[str] = new_result.replace("]", "").replace('"', "").replace("[", "").split(",")
        return self._prepare_data_end_battle(fexp)

    def _write_log(self) -> None:
        """Write log to console"""
        part1 = f"inu-{self._inu} inb-{self._inb} ina-{self._ina}"
        part2 = f" my_od-{self._my_od} my_mp-{self._my_mp}"
        part3 = f" my_hp-{self._my_hp}"
        text = part1 + part2 + part3
        logger.debug(text)

    def _logic(self) -> dict[str, str]:
        """Get data to do request

        :return: query data
        :rtype: dict[str, str]
        """
        self._my_od, self._my_mp, self._my_hp = self._fight_class.get_state()

        self._fight_class.fight()
        data = self._fight_class.get_queries_param()
        self._inu = data.inu
        self._inb = data.inb
        self._ina = data.ina

        self._write_log()
        return self._fight_class.get_data()

    def _create_fight_data(self) -> dict[str, str]:
        """Parse FIGHT

        :param fight_iteration: number of moves
        :type fight_iteration: int
        :return: data to request
        :rtype: dict[str, str]
        """
        self._check_alive()
        if self._is_end_battle():
            return self._create_end_battle_data()

        self._fight_class.setup_value(self._connect.get_html_page_text())

        return self._logic()

    def _stop_or_hit(self) -> None:
        """Check stop battle

        :param fight_iteration: number of moves
        :type fight_iteration: int
        """
        data = self._create_fight_data()
        if "post_id" in data.keys():
            self._connect.post_html(URL_MAIN, data)
        elif "retry" in data.keys():
            logger.debug("retry")
            self._connect.get_html(URL_MAIN)
        else:
            logger.info("Request for the end battle")
            self._connect.get_html(URL_MAIN, data)
            self._continue_fight = False

    def _is_error(self) -> bool:
        """Check error

        :return: is error
        :rtype: bool
        """
        error = re.findall(FIND_ERROR, self._connect.get_html_page_text())
        if error:
            return True
        return False

    def _reconnect(self) -> None:
        """Relogin"""
        logger.trace("\nNEED RELOGIN!!!")
        logger.trace("DO RELOGIN!!!\n")
        self._connect.reconnect()

    @timing_decorator
    def _run_fight(self) -> None:
        """Fight while"""
        fight_iteration = 0
        start_time = time.perf_counter()

        self._continue_fight = True
        while self._continue_fight:
            if self._is_error():
                self._reconnect()
            self._stop_or_hit()
            fight_iteration += 1
            start_time = check_iter(fight_iteration, start_time)

    def _change_location(self, location: Location) -> None:
        """Change location

        :param location: destination
        :type location: Location
        """
        self._person_location.go_to_location(location)

    def bait(self) -> str:
        """Start bait

        :return: result
        :rtype: str
        """
        self._person_chat.send_chat_message_to_telegram()
        if self._person_location.location == Location.FIGHT:
            self._run_fight()
        self._change_location(Location.ELIXIR)
        self.ab_while()
        text = f"{self._nickname} All Done"
        send_telegram(text)
        return text

    def _summon_bot(self, bot_type: SummonBotType) -> None:
        if self._retry == 3:
            logger.warning("No bot anywhere")
            return
        if self._retry == 2:
            bot_type.change_bot()
        self._use(item=bot_type.name)
        if FIND_FIGHT in self._connect.get_html_page_text():
            logger.success(f"IN fight {bot_type.name}")
            self._run_fight()
        else:
            self._retry += 1
            self._summon_bot(bot_type)

    def ab_while(self) -> None:
        """Start while"""
        while True:
            if self._iter_number > COUNT_ITER:
                break
            logger.warning(f"{self._iter_number=}")

            if self._person_location.location == Location.FIGHT:
                self._run_fight()
            self._change_location(Location.ELIXIR)

            if self._my_hp < START_HP or self._my_mp < START_MP:
                self._use(item=Elixir.ELIXIR_OF_RESTORATION.value)

            self._retry = 0
            # bot_type = SummonBotType(first_item=Summon.PLANAR, second_item=Summon.BAIT)
            bot_type = SummonBotType(first_item=Summon.BAIT, second_item=Summon.BAIT)
            self._summon_bot(bot_type)

            if self._iter_number % 50 == 0:
                logger.success(f"{self._iter_number=}")
                self._person_chat.send_chat_message_to_telegram()

            self._iter_number += 1

    @timing_decorator
    def _use(self, *, item: str) -> None:
        """Use something like HP/MP

        :param item: using item num
        :type item: str
        """
        pattern = FIND_USE_ITEM_PART1 + item + FIND_USE_ITEM_PART2
        results: list[str] = re.findall(pattern, self._connect.get_html_page_text())
        if results:
            for string in results:
                arg_lst = string.replace(r"' }", "").split("&")
            try:
                data = {
                    "get_id": 43,
                    "act": item,
                    "uid": arg_lst[0],
                }
                for item in arg_lst[1:]:
                    key, value = item.split("=")
                    data[key] = value

                self._connect.get_html(URL_MAIN, data=data)
            except UnboundLocalError:
                logger.error(f"{results=}")
                logger.error(f"{pattern=}")
                logger.error(f"{item=}")
                logger.critical("\n Fight on nature with bots\n")
                self._run_fight()
                self._change_location(Location.ELIXIR)
                self._use(item=item)
        else:
            text = f"\n No item {item}\n"
            logger.critical(text)
            send_telegram(text)
