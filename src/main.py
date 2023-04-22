from time import perf_counter

from loguru import logger

from config import NICKNAME
from config import PROXIES
from config import PROXY
from config import PROXY_IP

from dungeon_new import Game

from person_location import PersonLocation

from person_chat import PersonChat

from fight import Fight

from request import Connection
from request import my_ip
from request import send_telegram


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
    ip = get_current_ip()

    if PROXY_IP in ip:
        logger.info(f"\n-------ip------- {ip} LOGIN {NICKNAME}" * 5)
    else:
        raise Exception("Wrong IP")


@logger.catch
def main():

    check_ip()

    connect = Connection(PROXY)
    fight = Fight()
    person_location = PersonLocation(connect=connect)
    person_chat = PersonChat(connect=connect)
    game = Game(
        fight=fight, connect=connect, person_location=person_location, person_chat=person_chat, nickname=NICKNAME
    )

    logger.success("\n\nGame start!!!\n")

    game.bait()

    logger.success("That's all")


if __name__ == "__main__":
    logger.add("main.log", format="{time} {level} {message}", level="TRACE", rotation="10 MB", compression="zip")

    try:
        start_time = perf_counter()
        main()
        logger.success(f"timer {perf_counter()- start_time:.5f} seconds")
    except Exception as error:
        text = f"{NICKNAME} - trouble!!!"
        logger.error(error)
        send_telegram(text)
