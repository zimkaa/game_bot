from typing import Any

import pytest
import responses
from responses import matchers


EXAMPLE_IP = "127.0.0.100"

responses_attributes = {
    "method": responses.GET,
    "status": 200,
}

tests_list = (
    (
        responses_attributes,
        EXAMPLE_IP,
    ),
)


@responses.activate
@pytest.mark.parametrize("responses_attributes, expected", tests_list)
def test_ip(mock_env_user, responses_attributes: dict[str, Any], expected: str):
    # TODO need to refactor. Inherit class Player with settings
    from src.request import my_ip
    from src.config import CHECKER_IP_SITE

    responses_attributes.update({"body": expected})
    responses_attributes.update({"url": CHECKER_IP_SITE})
    responses.add(**responses_attributes)
    ip = my_ip()
    assert ip == expected


proxies = {
    "http": "http://login:password@2.2.2.2:3000",
    "https": "https://login:password@2.2.2.2:3000",
}

tests_list_ip_with_proxy = (
    (
        responses_attributes,
        EXAMPLE_IP,
        proxies,
    ),
)


@responses.activate
@pytest.mark.parametrize("responses_attributes, expected, proxies", tests_list_ip_with_proxy)
def test_ip_with_proxy(mock_env_user, responses_attributes: dict[str, Any], expected: str, proxies: dict[str, str]):
    # TODO need to refactor. Inherit class Player with settings
    from src.request import my_ip
    from src.config import CHECKER_IP_SITE

    responses_attributes.update({"body": expected})
    responses_attributes.update({"url": CHECKER_IP_SITE})

    responses.add(
        **responses_attributes,
        match=[matchers.request_kwargs_matcher({"proxies": proxies})],
    )
    ip = my_ip(proxies)
    assert ip == expected
