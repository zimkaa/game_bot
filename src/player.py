from typing import Any


class Player:
    def __init__(
        self,
        *,
        nickname: str,
        login: str | bytes,
        password: str,
        proxy: bool = False,
        proxy_ip: str = "",
        proxy_login: str = "",
        proxy_password: str = "",
        proxy_port: int = 0,
        tg_id: str = "",
        tg_token: str = "",
    ) -> None:
        self._nickname = nickname
        self._login = login
        self.__password = password
        self._proxy = proxy
        self._proxy_ip = proxy_ip
        self._proxy_login = proxy_login
        self.__proxy_password = proxy_password
        self._proxy_port = proxy_port
        self._tg_id = tg_id
        self.__tg_token = tg_token

    def get_tg_info(self) -> dict[str, Any]:
        tg_info = {
            "tg_id": self._tg_id,
            "tg_token": self.__tg_token,
        }
        return tg_info

    def get_proxy_info(self) -> dict[str, Any]:
        proxy_info = {
            "proxy_ip": self._proxy_ip,
            "proxy_login": self._proxy_login,
            "proxy_password": self.__proxy_password,
            "proxy_port": self._proxy_port,
        }
        return proxy_info

    def get_player_info(self) -> dict[str, Any]:
        player_info = {
            "login": self._login,
            "password": self.__password,
        }
        return player_info

    def __repr__(self):
        repr_string = "Player("
        repr_string += f'nickname="{self._nickname}",'
        repr_string += f' login="{self._login}",'
        repr_string += f' proxy="{self._proxy}",'
        repr_string += f' proxy_ip="{self._proxy_ip}",'
        repr_string += f' proxy_port="{self._proxy_port}",'
        repr_string += f' tg_id="{self._tg_id}"'
        repr_string += ")"
        return repr_string

    @property
    def proxy(self) -> bool:
        return self._proxy

    @property
    def proxy_ip(self) -> str:
        return self._proxy_ip

    @property
    def proxies(self) -> dict[str, str]:
        proxies = {
            "http": f"http://{self._proxy_login}:{self.__proxy_password}@{self._proxy_ip}:{self._proxy_port}",
            "https": f"https://{self._proxy_login}:{self.__proxy_password}@{self._proxy_ip}:{self._proxy_port}",
        }
        return proxies

    @property
    def login_data(self) -> dict[str, Any]:
        login_data = {
            "player_nick": self.login,
            "player_password": self.__password,
        }
        return login_data

    @property
    def login(self) -> str | bytes:
        return self._login

    @property
    def nickname(self) -> str:
        return self._nickname

    @property
    def tg_id(self) -> str:
        return self._tg_id
