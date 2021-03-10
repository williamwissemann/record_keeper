import pytest

from record_keeper.app import on_message
from record_keeper import BOT
from tests.fixture.message.mock import MockMessage


MM = MockMessage()


@pytest.mark.asyncio
async def test_when_off():
    MM.content = "!deactivate record-keeper training-wheels"
    assert await on_message(MM)
    MM.content = "!up xp 1000"
    assert await on_message(MM) == None
    MM.content = "!activate training-wheels"
    assert await on_message(MM)
    MM.content = "!up xp 1000"
    assert await on_message(MM) == [BOT.HELP_PROMPT]


@pytest.mark.asyncio
async def test_up():
    MM = MockMessage()
    MM.content = "!activate re"
    assert await on_message(MM) == [
        "Valid listener's status have activated for this channel!"
    ]
    MM = MockMessage()
    MM.content = "!active"
    print(await on_message(MM))

    MM = MockMessage()
    MM.content = "!up xp 1000"

    assert await on_message(MM)


def test_ls():
    pass


def test_lb():
    pass


def test_uuid():
    pass


def test_delete():
    pass
