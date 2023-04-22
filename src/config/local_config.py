import os

from dotenv import load_dotenv

from .variable_names import MAG
from .variable_names import SOLO


load_dotenv()


START_HP = 5_000

START_MP = 8_000

COUNT_ITER = 300

START_ITER = 1

PERSON_ROLE = SOLO

PERSON_TYPE = MAG

CHANNEL_ID_FRIENDS = os.getenv("CHANNEL_ID_FRIENDS")

CHANNEL_ID_LEADER = os.getenv("CHANNEL_ID_LEADER")

CHECKER_IP_SITE = os.getenv("CHECKER_IP_SITE3", "http://ipinfo.io/ip")

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

NICKNAME = LOGIN

player_nick = LOGIN
player_password = PASSWORD

PROXY = False
PROXY_IP = os.getenv("PROXY_IP")

PROXY_LOGIN = os.getenv("PROXY_LOGIN")
PROXY_PASS = os.getenv("PROXY_PASS")

PROXY_PORT = os.getenv("PROXY_PORT")

CHANNEL_ID = os.getenv("CHANNEL_ID", "277594923")

TG_TOKEN = os.getenv("TG_TOKEN")

user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; \
rv:11.0) like Gecko"

HEADER = {"User-Agent": user_agent}

DATA = {
    "player_nick": LOGIN,
    "player_password": PASSWORD,
}

PROXIES = {
    "http": f"http://{PROXY_LOGIN}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}",
    "https": f"https://{PROXY_LOGIN}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}",
}
