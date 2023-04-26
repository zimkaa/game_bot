from typing import Any

from getpass import getpass
import langid
import validators

from .player import Player


langid.set_languages(["ru", "en"])


DEFAULT_MESSAGE = "Allow only digits. Try one more time"


def get_settings_from_user_input(proxy: bool, use_tg: bool) -> dict[str, Any]:
    data: dict[str, Any] = dict()
    nickname = set_nickname()
    data.update(nickname)
    login = set_login(nickname["nickname"])
    data.update(login)
    password = set_password()
    data.update(password)
    if use_tg:
        tg_id = set_tg_id()
        data.update(tg_id)
        tg_token = set_tg_token()
        data.update(tg_token)
    if proxy:
        proxy_ip = set_proxy_ip()
        data.update(proxy_ip)
        proxy_login = set_proxy_login()
        data.update(proxy_login)
        proxy_password = set_proxy_password()
        data.update(proxy_password)
        proxy_port = set_proxy_port()
        data.update(proxy_port)
    return data


def create_person(data: dict[str, Any]) -> Player:
    person = Player(**data)
    return person


def get_data_from_env_file(proxy: bool) -> dict[str, Any]:
    import os

    from dotenv import load_dotenv

    load_dotenv()

    nickname = os.getenv("LOGIN", "Example_login")
    login = set_login(nickname)
    password = os.getenv("PASSWORD", "Example_password")

    proxy_ip = os.getenv("PROXY_IP", "")
    proxy_login = os.getenv("PROXY_LOGIN", "")
    proxy_password = os.getenv("PROXY_PASS", "")
    proxy_port = int(os.getenv("PROXY_PORT", 0))

    tg_id = int(os.getenv("CHANNEL_ID", 0))
    tg_token = os.getenv("TG_TOKEN", "")

    data: dict[str, Any] = {
        "nickname": nickname,
        "password": password,
        "proxy": proxy,
        "proxy_ip": proxy_ip,
        "proxy_login": proxy_login,
        "proxy_password": proxy_password,
        "proxy_port": proxy_port,
        "tg_id": tg_id,
        "tg_token": tg_token,
    }
    data.update(login)
    return data


def set_nickname() -> dict[str, str]:
    nickname = input("Login: ")
    if not nickname:
        print("Empty login. Try one more time")
        nickname = set_nickname()["nickname"]
    return {"nickname": nickname}


def set_login(login: str) -> dict[str, str | bytes]:
    lang, _ = langid.classify(login)
    if lang == "ru":
        return {"login": login.encode("cp1251")}
    return {"login": login}


def set_password() -> dict[str, str]:
    password = getpass()
    return {"password": password}


def set_proxy_ip() -> dict[str, str]:
    proxy_ip = input("Proxy IP: ")
    if not validators.ip_address.ipv4(proxy_ip):
        print("Wrong IP address. Try one more time")
        proxy_ip = set_proxy_ip()["proxy_ip"]
    return {"proxy_ip": proxy_ip}


def set_proxy_login() -> dict[str, str]:
    proxy_login = input("Proxy login: ")
    return {"proxy_login": proxy_login}


def set_proxy_password() -> dict[str, str]:
    proxy_password = getpass("Proxy password: ")
    return {"proxy_password": proxy_password}


def convert_to_int(func, value, *, message: str = DEFAULT_MESSAGE) -> int:
    try:
        int_value = int(value)
    except ValueError:
        print(message)
        int_value = func()
    return int_value


def set_proxy_port() -> dict[str, int]:
    proxy_port = input("Proxy port: ")
    port = convert_to_int(set_proxy_port, proxy_port)
    return {"proxy_port": port}


def set_tg_id() -> dict[str, int]:
    tg_id = input("Your telegram id: ")
    correct_tg_id = convert_to_int(set_tg_id, tg_id)
    return {"tg_id": correct_tg_id}


def set_tg_token() -> dict[str, str]:
    tg_token = input("Your telegram token: ")
    return {"tg_token": tg_token}
