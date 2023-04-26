from typing import Any

from loguru import logger

import sentry_sdk

from .bot import main

from .initial_settings import create_person
from .initial_settings import get_data_from_env_file
from .initial_settings import get_settings_from_user_input

from .request import send_telegram


sentry_sdk.init(
    dsn="https://ac8aa8ca81124c569460f52305402573@o4505058793095168.ingest.sentry.io/4505058802597888",
    traces_sample_rate=1.0,
    environment="production",
)


def start(arguments: dict[str, Any]):
    proxy = arguments.get("use_proxy")
    if arguments.get("set_manual_settings"):
        use_tg = arguments.get("use_tg")
        data = get_settings_from_user_input(proxy, use_tg)
    else:
        data = get_data_from_env_file(proxy)

    person = create_person(data)

    try:
        main(person)
    except Exception as error:
        text = f"{person.nickname} - trouble!!!"
        sentry_sdk.capture_exception(error=error)
        logger.error(error)
        send_telegram(text)
