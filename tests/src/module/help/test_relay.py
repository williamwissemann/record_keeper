import pytest

from record_keeper.app import on_message
from tests.fixture.message.mock import MockMessage

MM = MockMessage()


@pytest.mark.asyncio
async def test_medals_prompt():
    MM.content = "!help"
    assert await on_message(MM)


@pytest.mark.asyncio
async def test_delete_prompt():
    MM.content = "!medals"
    assert await on_message(MM)
