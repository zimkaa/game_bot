import re
from enum import Enum
from typing import Callable

from loguru import logger

from .config import FIND_DISABLED  # noqa: I100s
from .config import FIND_FIGHT
from .config import FIND_FROM_NATURE_TO_INV
from .config import FIND_INVENTORY
from .config import FIND_IN_CITY
from .config import FIND_PAGE_INVENTORY
from .config import URL_MAIN

from .request import Connection


class Location(str, Enum):
    CITY = "CITY"
    FIGHT = "FIGHT"
    INVENTORY = "INVENTORY"
    NATURE = "NATURE"
    ELIXIR = "ELIXIR"
    INFO = "INFO"


class PersonLocation:
    def __init__(self, *, connect: Connection) -> None:
        self._connect = connect
        self._prepare: list[str]
        self._location: Location

    def go_to_location(self, destination: Location) -> None:
        if destination == self._location:
            logger.success("person already on needed location")
            return
        if destination == Location.ELIXIR:
            if self._location != Location.INVENTORY:
                self._go_to_inventory(self._location)
            self._from_inventory_go_to_elixir()
        else:
            raise NotImplementedError

    def _go_to_inventory(self, location: Location) -> None:
        location_to_inventory: dict[Location, Callable] = {
            Location.FIGHT: self._do_nothing,
            Location.CITY: self._from_city_go_to_inventory,
            Location.NATURE: self._from_nature_go_to_inventory,
            Location.INVENTORY: self._do_nothing,
            Location.ELIXIR: self._from_elixir_go_to_inventory,
            Location.INFO: self._from_info_go_to_inventory,
        }
        location_to_inventory[location]()

    @property
    def location(self) -> Location:
        self._where_i_am()
        return self._location

    def _is_fight(self, html: str) -> bool:
        if FIND_FIGHT in html:
            logger.success("in fight")
            self._prepare = list()
            self._location = Location.FIGHT
            return True
        return False

    def _is_nature(self, html: str) -> bool:
        if FIND_DISABLED not in html:
            logger.success("on nature")
            self._prepare = list()
            self._location = Location.NATURE
            return True
        return False

    def _is_inventory(self, html: str) -> bool:
        if FIND_INVENTORY in html:
            logger.success("in inventory")
            self._prepare = list()
            self._location = Location.INVENTORY
            return True
        return False

    def _is_city(self, html: str) -> bool:
        prepare = re.findall(FIND_IN_CITY, html)
        if prepare:
            logger.success("in city")
            self._prepare = prepare
            self._location = Location.CITY
            return True
        return False

    def _is_info(self, html: str) -> bool:
        prepare = re.findall(FIND_PAGE_INVENTORY, html)
        if prepare:
            self._prepare = prepare
            logger.success("in info")
            self._location = Location.INFO
            return True
        return False

    def _where_i_am(self) -> Location:
        """where i am

        :return: location where i am
        :rtype: Location
        """
        html = self._connect.get_html_page_text()

        self._prepare = list()

        # lst_method = [
        #     "_is_fight",
        #     "_is_info",
        #     "_is_city",
        #     "_is_inventory",
        #     "_is_nature",
        #     "_is_fight",
        # ]

        # for method_name in lst_method:
        #     method = getattr(self, method_name)
        #     if method(html):
        #         return self._location

        if self._is_fight(html):
            return Location.FIGHT

        if self._is_nature(html):
            return Location.NATURE

        if self._is_inventory(html):
            return Location.INVENTORY

        if self._is_city(html):
            return Location.CITY

        if self._is_info(html):
            return Location.INFO

        return Location.ELIXIR

    def _from_city_go_to_inventory(self) -> None:
        """construct the request and send it"""
        logger.success("in city")
        prepare = re.findall(FIND_IN_CITY, self._connect.get_html_page_text())
        vcode = prepare[0].split("=")[-1]
        data = {"get_id": "56", "act": "10", "go": "inv", "vcode": vcode}
        self._connect.get_html(URL_MAIN, data=data)

    def _from_nature_go_to_inventory(self) -> None:
        """construct the request and send it"""
        logger.success("in nature")
        prepare = re.findall(FIND_FROM_NATURE_TO_INV, self._connect.get_html_page_text())
        logger.debug(f"{prepare=}")
        if prepare:
            data = {"get_id": "56", "act": "10", "go": "inv", "vcode": prepare[0]}
            self._connect.get_html(URL_MAIN, data=data)

    def _from_info_go_to_inventory(self) -> None:
        """construct the request and send it"""
        logger.success("in info")
        if not self._prepare:
            logger.debug("self._prepare not exists")
            self._prepare = re.findall(FIND_PAGE_INVENTORY, self._connect.get_html_page_text())
        if self._prepare:
            vcode = self._prepare[0].split("=")[-1]
            data = {"get_id": "56", "act": "10", "go": "inv", "vcode": vcode}
            self._connect.get_html(URL_MAIN, data=data)
        else:
            logger.debug('_from_info_to_inventory not find ?<=&go=inv&vcode=).+(?=\'" value="Инвентарь')

    def _from_elixir_go_to_inventory(self) -> None:
        """construct the request and send it"""
        logger.success("in elixir")
        data = {"wca": "28"}
        self._connect.get_html(URL_MAIN, data=data)

    def _do_nothing(self) -> None:
        """Do nothing"""
        pass

    def _from_inventory_go_to_elixir(self) -> None:
        """construct the request and send it"""
        logger.success("go_to_elixir")
        data = {"im": "6"}
        self._connect.get_html(URL_MAIN, data=data)
