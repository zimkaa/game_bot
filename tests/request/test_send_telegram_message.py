from typing import Any

import pytest
import responses


responses_attributes = {
    "method": responses.POST,
    "status": 200,
}

tests_list = [
    responses_attributes,
]


@responses.activate
@pytest.mark.parametrize("responses_attributes", tests_list)
def test_send_telegram(mock_env_user, capsys, responses_attributes: dict[str, Any]):
    # TODO need to refactor. Inherit class Player with settings
    from src.request import send_telegram
    from src.config import TG_TOKEN

    url = "https://api.telegram.org/bot" + TG_TOKEN + "/sendMessage"
    responses_attributes.update({"url": url})
    responses.add(**responses_attributes)
    send_telegram("Example_text")

    out, _ = capsys.readouterr()
    assert out == ""


responses_attributes_fail = {
    "method": responses.POST,
    "status": 400,
}

tests_list_fail = [
    responses_attributes_fail,
]


@responses.activate
@pytest.mark.parametrize("responses_attributes_fail", tests_list_fail)
def test_send_telegram_fail(mock_env_user, capsys, responses_attributes_fail: dict[str, Any]):
    # TODO need to refactor. Inherit class Player with settings
    from src.request import send_telegram
    from src.config import TG_TOKEN

    url = "https://api.telegram.org/bot" + TG_TOKEN + "/sendMessage"
    responses_attributes_fail.update({"url": url})
    responses.add(**responses_attributes_fail)
    send_telegram("Example_text")

    out, _ = capsys.readouterr()
    assert out == "Some trouble with TG\n"
