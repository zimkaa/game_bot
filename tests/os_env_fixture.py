import pytest


@pytest.fixture(autouse=True)
def mock_env_user(monkeypatch):
    monkeypatch.setenv(
        "CHECKER_IP_SITE",
        "http://testip.example",
    )
    monkeypatch.setenv(
        "TG_TOKEN",
        "example:token",
    )
    monkeypatch.setenv(
        "CHANNEL_ID",
        "1111111",
    )
