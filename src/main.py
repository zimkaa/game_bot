from time import perf_counter
from time import sleep

from loguru import logger

from config import NICKNAME
from config import PROXIES
from config import PROXY
from config import PROXY_IP
from dungeon_new import Game
from fight import Fight
from request import Connection
from request import my_ip
from request import send_telegram


def check_ip():
    if PROXY:
        ip = my_ip(PROXIES)
    else:
        ip = my_ip()

    if PROXY_IP in ip:
        logger.info(f"\n-------ip------- {ip} LOGIN {NICKNAME}" * 5)


@logger.catch
def main():

    check_ip()

    connect = Connection(PROXY)
    fight = Fight()
    game = Game(fight=fight, connect=connect)

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
        text = f"{NICKNAME} - БЕДА ВСЕ УПАЛО!!!"
        logger.error(error)
        send_telegram(text)
        sleep(5)
        send_telegram(text)
