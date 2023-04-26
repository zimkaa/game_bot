from loguru import logger

from .fight import Fight

from .game import Game

from .person_chat import PersonChat

from .person_location import PersonLocation

from .player import Player

from .request import Connection
from .request import my_ip


logger.add(
    "main.log",
    format="{time} {level} {message}",
    level="TRACE",
    rotation="10 MB",
    compression="zip",
)


def get_current_ip(person: Player) -> str:
    """Get current IP

    :return: string IP
    :rtype: str
    """
    if person.proxy:
        return my_ip(person.proxies)
    return my_ip()


def check_ip(person: Player):
    """Check current IP

    :raises Exception: wrong IP
    """
    if person.proxy:
        ip = get_current_ip(person)

        if person.proxy_ip in ip:
            logger.info(f"\n-------ip------- {ip} LOGIN {person.nickname}" * 5)
        else:
            raise Exception("Wrong IP")


def start_bot(person: Player):

    check_ip(person)

    connect = Connection(person)
    fight = Fight(nickname=person.nickname)
    person_location = PersonLocation(connect=connect)
    person_chat = PersonChat(connect=connect, nickname=person.nickname)
    game = Game(
        fight=fight,
        connect=connect,
        person_location=person_location,
        person_chat=person_chat,
        nickname=person.nickname,
    )

    logger.success("\n\nGame start!!!\n")

    game.bait()

    logger.success("That's all")
