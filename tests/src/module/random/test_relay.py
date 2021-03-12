import pytest
import mock

from record_keeper.app import on_message
from tests.fixture.message.mock import MockMessage

MM = MockMessage()

@pytest.mark.asyncio
async def test_roll():
    with mock.patch("asyncio.sleep", return_value=None):
        MM.content = "!roll"
        assert "mock_author_name rolled" in (await on_message(MM))[0]

        MM.content = "!roll 1000"
        assert "1000" in (await on_message(MM))[0]

@pytest.mark.asyncio
async def test_d20():
    with mock.patch("asyncio.sleep", return_value=None):
        MM.content = "!d20"
        assert "mock_author_name rolled" in (await on_message(MM))[0]
