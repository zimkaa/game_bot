from typing import Any

import pytest
import responses


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
def test_normal(mock_env_user, responses_attributes: dict[str, Any], expected: str):
    # TODO need to refactor. Inherit class Player with settings
    from src.request import my_ip
    from src.config import CHECKER_IP_SITE

    responses_attributes.update({"body": expected})
    responses_attributes.update({"url": CHECKER_IP_SITE})
    responses.add(**responses_attributes)
    ip = my_ip()
    assert ip == expected
