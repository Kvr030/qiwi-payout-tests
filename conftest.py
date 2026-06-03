import pytest
import os


@pytest.fixture(scope="session")
def base_url():
    return "https://edge.qiwi.com"


@pytest.fixture(scope="session")
def token():
    return os.getenv("QIWI_TOKEN", "YOUR_TOKEN_HERE")


@pytest.fixture(scope="session")
def headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="session")
def test_account():
    return os.getenv("TEST_ACCOUNT", "TEST_ACCOUNT_NUMBER")