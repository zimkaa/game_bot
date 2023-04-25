from loguru import logger

import sentry_sdk

from config import NICKNAME  # noqa: I100
from config import PROXIES
from config import PROXY
from config import PROXY_IP

from dungeon_new import Game

from fight import Fight

from person_chat import PersonChat

from person_location import PersonLocation

from request import Connection
from request import my_ip
from request import send_telegram


sentry_sdk.init(
    dsn="https://ac8aa8ca81124c569460f52305402573@o4505058793095168.ingest.sentry.io/4505058802597888",
    traces_sample_rate=1.0,
    environment="production",
)

logger.add(
    "main.log",
    format="{time} {level} {message}",
    level="TRACE",
    rotation="10 MB",
    compression="zip",
)


def get_current_ip() -> str:
    """Get current IP

    :return: string IP
    :rtype: str
    """
    if PROXY:
        return my_ip(PROXIES)
    return my_ip()


def check_ip():
    """Check current IP

    :raises Exception: wrong IP
    """
    if PROXY:
        ip = get_current_ip()

        if PROXY_IP in ip:
            logger.info(f"\n-------ip------- {ip} LOGIN {NICKNAME}" * 5)
        else:
            raise Exception("Wrong IP")


def main():

    check_ip()

    connect = Connection(PROXY)
    fight = Fight(nickname=NICKNAME)
    person_location = PersonLocation(connect=connect)
    person_chat = PersonChat(connect=connect)
    game = Game(
        fight=fight,
        connect=connect,
        person_location=person_location,
        person_chat=person_chat,
        nickname=NICKNAME,
    )

    logger.success("\n\nGame start!!!\n")

    game.bait()

    logger.success("That's all")


def start():
    try:
        main()
    except Exception as error:
        text = f"{NICKNAME} - trouble!!!"
        sentry_sdk.capture_exception(error=error)
        logger.error(error)
        send_telegram(text)
