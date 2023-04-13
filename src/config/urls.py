import os

from dotenv import load_dotenv


load_dotenv()

URL = os.getenv("URL", "http://neverlands.ru")
URL_GAME = URL + os.getenv("URL_GAME", "/game.php")
URL_MAIN = URL + os.getenv("URL_MAIN", "/main.php")
URL_EVENT = URL + os.getenv("URL_EVENT", "/gameplay/ajax/event.php")
URL_KEEP_CONNECTION = URL + os.getenv("URL_KEEP_CONNECTION", "/ch.php?{rand_float}&show=1&fyo=0")
URL_PLAYER_INFO = URL + os.getenv("PLAYER_INFO_URL", "/pinfo.cgi?")
URL_SCROLLS_INV = URL_MAIN + os.getenv("SCROLLS_INV", "?wca=28")
