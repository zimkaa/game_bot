import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from loguru import logger
import requests  # noqa: I201

from ..config import CHANNEL_ID  # noqa: I100
from ..config import CHECKER_IP_SITE
from ..config import DATA
from ..config import HEADER
from ..config import NICKNAME
from ..config import PROXIES
from ..config import TG_TOKEN
from ..config import URL
from ..config import URL_GAME
from ..config import URL_MAIN


logging.basicConfig(
    level=logging.DEBUG,
    handlers=[RotatingFileHandler("request.log", maxBytes=5_242_880, backupCount=10)],
    format="%(asctime)s:%(levelname)s:%(filename)s:%(message)s",
)
standard_logger = logging.getLogger("request_to_nl")

logging.getLogger("urllib3").setLevel("WARNING")


class Connection:
    def __init__(self, proxy: bool = False) -> None:
        self.result: requests.models.Response
        self._set_session(proxy)
        self._log_in()

    def reconnect(self) -> None:
        self._log_in()

    def get_result(self) -> requests.models.Response:
        """Return class Response from module requests

        :return: class Response
        :rtype: requests.models.Response
        """
        return self.result

    def make_file(self, text: str, reason: str) -> None:
        """
        Write data to file
        """
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        dir_path = Path(__file__).parent.resolve()
        file_name = f"{now}_{reason}"
        file_path = os.path.join(dir_path, "files", f"{file_name}.txt")

        with open(file_path, "w") as file:
            file.write(text)

    def get_html_page_text(self) -> str:
        return self.result.text

    def _set_session(self, proxy: bool = False) -> None:
        """
        Set session
        """
        self.session = requests.Session()
        if proxy:
            self.session.proxies.update(PROXIES)
        self.session.headers.update(HEADER)

    def _log_in(self) -> None:
        """
        Logging to game

        Also can used to relogin
        """
        self.get_html(URL)
        self.post_html(URL_GAME, DATA)
        self.result = self.get_html(URL_MAIN)

    def get_html(self, site_url: str, data: dict = None) -> requests.models.Response:
        """
        Executing a get request
        """
        call_num = 0

        def _retry(data):
            nonlocal call_num
            call_num += 1
            standard_logger.debug(f"get_html {NICKNAME} request send {call_num=} times {data=} {site_url=}")
            if call_num >= 3:
                content = self.result.headers.get("Content-Type")
                standard_logger.error(f"get_html {NICKNAME} call_num >= 3 {call_num=} {content=}")
                text = f"{NICKNAME}----get_html--error code: {self.result.status_code}"
                logger.error(f"{text=}")
                send_telegram(text)
                raise Exception(text)
            self.result = self.session.get(site_url, params=data)
            content = self.result.headers.get("Content-Type")
            if self.result.status_code == 200:
                return self.result
            elif self.result.status_code == 502:
                text = f"{NICKNAME} Error get_html {self.result.status_code}"
                send_telegram(text)
                logger.error(f"Retry GET query 502 {text=} and {data=} and {site_url=}")
                standard_logger.warning(f"Retry GET query 502 {text=} and {data=} and {site_url=}")
                standard_logger.error(f"{NICKNAME} get_html something new {call_num=} {content=}")
                raise Exception(text)
            elif self.result.status_code == 546:
                standard_logger.debug(f"{site_url=}")
                text = f"{NICKNAME} get_htmlError {self.result.status_code} {content=} {call_num=}"
                standard_logger.error(text)
                send_telegram(text)
                standard_logger.warning(f"{NICKNAME} Retry GET query 546 {text=} and {data=} and {site_url=}")
                logger.error(f"{NICKNAME} Retry GET query 546 {text=} and {data=} and {site_url=}")
                standard_logger.error(f"{NICKNAME} get_html something new {call_num=} {content=}")
                raise Exception(text)
            else:
                text = f"{NICKNAME} ---get_html--error code: {self.result.status_code}"
                send_telegram(text)
                standard_logger.error(f"{NICKNAME} get_html something new {call_num=} {content=}")
                raise Exception(text)

        try:
            _retry(data)
            return self.result
        except Exception as error:
            standard_logger.warning(f"{NICKNAME} {self.result.status_code=}")
            standard_logger.warning(f"{NICKNAME} {site_url=}")
            standard_logger.warning(f"{NICKNAME} {type(data)} {data=}")
            standard_logger.warning(f"{NICKNAME} {self.result.text=}")
            standard_logger.warning(f"{NICKNAME} {self.result.content=}")
            standard_logger.warning(f"{NICKNAME} {self.result.headers=}")
            standard_logger.warning(f"{NICKNAME} {self.result.reason=}")
            standard_logger.warning(f"{NICKNAME} {self.result.request.body=}")
            text = f"{NICKNAME} get_html something new {error=}"
            logger.error(text)
            send_telegram(text)
            raise Exception(text)

    def post_html(self, site_url: str, data: dict = None) -> requests.models.Response:
        """
        Executing a post request
        """
        call_num = 0

        def _retry(data):
            nonlocal call_num
            call_num += 1
            standard_logger.debug(f"{NICKNAME} post_html request send {call_num=} times {data=} {site_url=}")
            if call_num >= 3:
                content = self.result.headers.get("Content-Type")
                standard_logger.debug(f"{NICKNAME} post_html call_num >= 3 {call_num=} {content=}")
                text = f"{NICKNAME}---post_html--error code: {self.result.status_code}"
                logger.error(f"{text=}")
                send_telegram(text)
                raise Exception(text)
            self.result = self.session.post(site_url, data=data)
            content = self.result.headers.get("Content-Type")
            if self.result.status_code == 200:
                return self.result
            elif self.result.status_code == 502:
                text = f"{NICKNAME} post_html Error {self.result.status_code=} {content=}"
                standard_logger.error(f"{NICKNAME} Retry POST query 502 {data=} and {site_url=}")
                send_telegram(text)
                logger.error(f"{NICKNAME} Retry POST query 502 {data=} and {site_url=}")
                raise Exception(text)
            else:
                text = f"{NICKNAME} ---post_html--error code: {self.result.status_code=}  {content=}"
                send_telegram(text)
                standard_logger.error(f"post_html something new  {call_num=}")
                raise Exception(text)

        try:
            _retry(data)
            return self.result
        except Exception as error:
            standard_logger.warning(f"{NICKNAME} {self.result.status_code=}")
            standard_logger.warning(f"{NICKNAME} {site_url=}")
            standard_logger.warning(f"{NICKNAME} {type(data)} {data=}")
            standard_logger.warning(f"{NICKNAME} {self.result.text=}")
            standard_logger.warning(f"{NICKNAME} {self.result.content=}")
            standard_logger.warning(f"{NICKNAME} {self.result.headers=}")
            standard_logger.warning(f"{NICKNAME} {self.result.reason=}")
            standard_logger.warning(f"{NICKNAME} {self.result.request.body=}")
            text = f"{NICKNAME} post_html something new -{error=}"
            logger.error(text)
            send_telegram(text)
            raise Exception(text)


def send_telegram(text: str) -> None:
    if CHANNEL_ID:
        method = "https://api.telegram.org/bot" + TG_TOKEN + "/sendMessage"  # type: ignore
        result = requests.post(
            method,
            data={
                "chat_id": CHANNEL_ID,  # type: ignore
                "text": text,  # type: ignore
            },
        )
        logger.debug(f"{CHANNEL_ID=}")
        if result.status_code != 200:
            logger.critical("Some trouble with TG")


def my_ip(proxies: dict = None) -> str:
    """
    Do request to get IP (need to check proxy)
    """
    answer = requests.get(CHECKER_IP_SITE, headers=HEADER, proxies=proxies)  # type: ignore
    if answer.status_code != 200:
        text = "PROXY DON'T RESPONSE!!!"
        send_telegram(text)
        raise Exception(text)
    return answer.text
