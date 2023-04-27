import pytest


@pytest.fixture(autouse=True)
def mock_env_user(monkeypatch):
    monkeypatch.setenv(
        "CHECKER_IP_SITE",
        "http://testip.example",
    )
