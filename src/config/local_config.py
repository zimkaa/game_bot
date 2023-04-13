import os

from dotenv import load_dotenv

from .variable_names import SOLO
from .variable_names import SLAVE
from .variable_names import LEADER
from .variable_names import MAG
from .variable_names import WARRIOR
from .variable_names import HUNTER
from .variable_names import ROMANSON
from .variable_names import TURNOFF
from .variable_names import ANGEL


load_dotenv()

# SIEGE = True
SIEGE = False

PERSON_ROLE = SOLO
# PERSON_ROLE = SLAVE
# PERSON_ROLE = LEADER

# LEADER_TYPE = WARRIOR
LEADER_TYPE = MAG

# LEADER_NAME = ROMANSON
# LEADER_NAME = HUNTER
LEADER_NAME = ANGEL

MAG_KILLER = True
# MAG_KILLER = False

PERSON_TYPE = MAG
# PERSON_TYPE = WARRIOR

# PARTY_MEMBERS = [ANGEL, HUNTER]
# PARTY_MEMBERS = [ANGEL, ROMANSON]
PARTY_MEMBERS = [ANGEL, HUNTER, ROMANSON]

# MAG_DAMAGER = TURNOFF
# MAG_DAMAGER = HUNTER
MAG_DAMAGER = ANGEL

DEAD_PLAGUE_ZOMBIE = "0/125"

LEN_PARTY = len(PARTY_MEMBERS)

CHECKER_IP_SITE = os.getenv("CHECKER_IP_SITE3", "http://ipinfo.io/ip")

FIGHT_ITERATIONS = 5

SLEEP_TIME = os.getenv("SLEEP_TIME", 5)

SLEEP_TIME_PER_HIT = os.getenv("SLEEP_TIME_PER_HIT", 0.5)

# FIGHT_TEST_MODE = True  # ON
FIGHT_TEST_MODE = False  # OFF


AUTO_BUFF = True  # ON
# AUTO_BUFF = False  # OFF

AB = True
# AB = False

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

NICKNAME = LOGIN.decode("cp1251") if isinstance(LOGIN, bytes) else LOGIN

player_nick = LOGIN
player_password = PASSWORD


PROXY = False  # without proxy
PROXY_IP = os.getenv("PROXY_IP_225")  # without proxy
# PROXY = True  # with proxy
# PROXY_IP = os.getenv("PROXY_IP")  # with proxy

PROXY_LOG = os.getenv("PROXY_LOG")
PROXY_PASS = os.getenv("PROXY_PASS")

PROXY_PORT = os.getenv("PROXY_PORT")

CITY = "2"

TELEPORT_CITY = 2  # OKTAL

CHANNEL_ID = os.getenv("CHANNEL_ID", "277594923")

CHANNEL_ID_FRIENDS = os.getenv("CHANNEL_ID_FRIENDS")

CHANNEL_ID_ROMANSON = os.getenv("CHANNEL_ID_ROMANSON")

CHANNEL_ID_HUNTER = os.getenv("CHANNEL_ID_HUNTER")

CHANNEL_ID_TURNOFF = os.getenv("CHANNEL_ID_TURNOFF")

CHANNEL_ID_ANGEL = os.getenv("CHANNEL_ID_ANGEL")

CHANNEL_ID_DICT = {
    ROMANSON: CHANNEL_ID_ROMANSON,
    HUNTER: CHANNEL_ID_HUNTER,
    TURNOFF: CHANNEL_ID_TURNOFF,
    ANGEL: CHANNEL_ID_ANGEL,
}

if PERSON_ROLE == SLAVE:
    CHANNEL_ID_LEADER = CHANNEL_ID_DICT.get(LEADER_NAME)
else:
    CHANNEL_ID_LEADER = ""

TG_TOKEN = os.getenv("TG_TOKEN")

user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; \
rv:11.0) like Gecko"

HEADER = {"User-Agent": user_agent}

DATA = {
    "player_nick": LOGIN,
    "player_password": PASSWORD,
}

PROXIES = {
    "http": f"http://{PROXY_LOG}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}",
    "https": f"https://{PROXY_LOG}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}",
}
