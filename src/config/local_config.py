import os

from dotenv import load_dotenv

from .variable_names import MAG


load_dotenv()


START_HP = 2_000

START_MP = 4_200

COUNT_ITER = 3

START_ITER = 1

PERSON_TYPE = MAG

CHECKER_IP_SITE = os.getenv("CHECKER_IP_SITE3", "http://ipinfo.io/ip")

CHANNEL_ID = os.getenv("CHANNEL_ID")

TG_TOKEN = os.getenv("TG_TOKEN")

user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; \
rv:11.0) like Gecko"

HEADER = {"User-Agent": user_agent}
