import mock
import pytest

from record_keeper import BOT
from record_keeper.__main__ import on_message
from tests.fixture.client.mock import Client
from tests.fixture.message.mock import MockMessage

mm = MockMessage()


@pytest.mark.asyncio
async def test_when_off():
    mm.content = "!deactivate record-keeper training-wheels"
    assert await on_message(mm)
    mm.content = "!up xp 1000"
    assert await on_message(mm) is None
    mm.content = "!activate training-wheels"
    assert await on_message(mm)
    mm.content = "!up xp 1000"
    assert await on_message(mm) == [BOT.HELP_PROMPT]


@pytest.mark.asyncio
async def test_up():
    mm.content = "!activate record-keeper"
    assert await on_message(mm) == [
        "Valid listener's status have activated for this channel!"
    ]
    mm.content = "!active"
    assert await on_message(mm)

    mm.content = "!up xp 123456"
    assert "123456" in (await on_message(mm))[0]

    mm.content = "!up xp 898900"
    assert "898900" in (await on_message(mm))[0]

    mm.content = "!up xp 1990 date:1990-10-10"
    assert "1990-10-10" in (await on_message(mm))[0]

    with mock.patch("record_keeper.BOT.client", Client()):
        mm.content = "!up xp 898901 date:1990-10-11 user:tester"
        assert "<@!tester>" in (await on_message(mm))[0]


@pytest.mark.asyncio
async def test_ls():
    mm.content = "!ls"
    assert await on_message(mm) == [BOT.HELP_PROMPT]

    mm.content = "!ls xp"
    assert "898900" in (await on_message(mm))[0]

    with mock.patch("record_keeper.BOT.client", Client()):
        mm.content = "!ls xp test"
        response = (await on_message(mm))[0]
        assert "tester" in response
        assert "1990-10-11" in response
        assert "898901" in response


@pytest.mark.asyncio
async def test_lb():
    mm.content = "!lb"
    assert await on_message(mm) == [BOT.HELP_PROMPT]

    with mock.patch("record_keeper.BOT.client", Client()):
        mm.content = "!lb xp"
        response = (await on_message(mm))[0]
        assert "898900" in response
        assert "898901" in response


@pytest.mark.asyncio
async def test_uuid():
    mm.content = "!uuid"
    assert await on_message(mm) == [BOT.HELP_PROMPT]

    mm.content = "!uuid xp"
    response = (await on_message(mm))[0]
    assert "898900" in response
    assert "123456" in response


@pytest.mark.asyncio
async def test_delete():
    mm.content = "!uuid xp"
    response = (await on_message(mm))[0]

    for uuid in response.split("\n")[3:]:
        mm.content = f"!del xp {uuid}"
        response = (await on_message(mm))[0]

    mm.content = "!ls xp"
    response = (await on_message(mm))[0]
    assert "898900" not in response
    assert "123456" not in response
