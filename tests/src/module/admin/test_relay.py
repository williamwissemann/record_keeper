import pytest

from record_keeper.__main__ import on_message
from tests.fixture.message.mock import MockMessage

MM = MockMessage()

MSG_ACTIVE = "Valid listener's status have activated for this channel!"
MSG_DEACTIVATED = "Valid listener's status have deactivated for this channel!"


@pytest.mark.asyncio
async def test_setup():
    MM.content = "!setup"
    assert await on_message(MM)


@pytest.mark.asyncio
async def test_activate_all():
    MM.content = "!activate default"
    assert await on_message(MM) == [MSG_ACTIVE]
    MM.content = "!activate all"
    assert await on_message(MM) == [MSG_ACTIVE]

    MM.content = "!active"
    response_list = await on_message(MM)
    assert "training-wheels" in response_list[0]


@pytest.mark.asyncio
async def test_deactivate_reactivate_one():
    MM.content = "!deactivate training-wheels"
    assert await on_message(MM) == [MSG_DEACTIVATED]

    MM.content = "!active"
    assert "training-wheels" not in await on_message(MM)

    MM.content = "!deactivate training-wheels"
    assert await on_message(MM) == [MSG_DEACTIVATED]

    MM.content = "!activate training-wheels"
    assert await on_message(MM) == [MSG_ACTIVE]

    MM.content = "!active"
    response_list = await on_message(MM)
    assert "training-wheels" in response_list[0]
