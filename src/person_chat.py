import random
import re

from loguru import logger

from config import FIND_CHAT  # noqa: I100
from config import FIND_MESSAGE_FOR_PERSON
from config import FIND_MESSAGE_TEXT
from config import FIND_SENDER_NAME
from config import NICKNAME
from config import URL_KEEP_CONNECTION

from request import Connection
from request import send_telegram


FINDER_CHAT = re.compile(FIND_CHAT)

FINDER_MESSAGE_FOR_PERSON = re.compile(FIND_MESSAGE_FOR_PERSON)

FINDER_SENDER_NAME = re.compile(FIND_SENDER_NAME)

FINDER_MESSAGE_TEXT = re.compile(FIND_MESSAGE_TEXT)


class PersonChat:
    def __init__(self, *, connect: Connection) -> None:
        self._connect = connect
        self._messages: list[str]

    def send_chat_message_to_telegram(self):
        self._get_chat()
        if not self._is_empty_chat():
            if text := self._prepare_message_for_person(self._messages):
                logger.error(text)
                send_telegram(text)
        self._messages = list()

    def _get_chat(self) -> None:
        """Get chat"""
        url = URL_KEEP_CONNECTION.format(rand_float=random.random())
        self._connect.get_html(url)

    def _is_empty_chat(self) -> bool:
        text_string = self._connect.get_html_page_text()
        self._messages = FINDER_CHAT.findall(text_string)
        logger.info(f"_is_empty_chat {self._messages=}")
        if self._messages:
            return False
        return True

    def _prepare_message_for_person(self) -> str:
        """Send messages for person

        :param messages: list message
        :type messages: list[str]
        """
        text_for_message = ""
        for mes in self._messages:
            text = FINDER_MESSAGE_FOR_PERSON.findall(mes)
            if text:
                if NICKNAME in str(text[0]):
                    sender_name = FINDER_SENDER_NAME.findall(str(text[0]))
                    if sender_name:
                        only_text = FINDER_MESSAGE_TEXT.findall(mes)
                        text_for_message = (
                            f"Игроку {NICKNAME} пишут в чат!\nОтправитель: {sender_name[0]} --- {only_text[0]}"
                        )
        return text_for_message
