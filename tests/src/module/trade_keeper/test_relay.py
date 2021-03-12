import pytest
import mock

from record_keeper import BOT
from record_keeper.app import on_message
from tests.fixture.client.mock import Client
from tests.fixture.message.mock import MockMessage

mm = MockMessage()


@pytest.mark.asyncio
async def test_want():
    mm.content = "!want 10"
    assert await on_message(mm)

    mm.content = "!want 11"
    assert await on_message(mm)

    mm.content = "!want 12"
    assert await on_message(mm)

    mm.content = "!want 30"
    assert await on_message(mm)

    mm.content = "!want 40"
    assert '10-12,30,40' in (await on_message(mm))[0]


@pytest.mark.asyncio
async def test_unwant():
    mm.content = "!unwant 11"
    assert (await on_message(mm))[0]


@pytest.mark.asyncio
async def test_tbs():
    mm.content = "!tbs"
    assert '10,12,30,40' in (await on_message(mm))[0]


@pytest.mark.asyncio
async def test_tbp():
    with mock.patch('record_keeper.BOT.client', Client()):
        mm.content = "!tbp 10"
        assert 'bidoof' in (await on_message(mm))[0]


@pytest.mark.asyncio
async def test_tbu():
    with mock.patch('record_keeper.BOT.client', Client()):
        mm.content = "!tbu test"
        assert 'Bidoof' in (await on_message(mm))[0]

@pytest.mark.asyncio
async def test_special():
    mm.content = "!special 10"
    assert await on_message(mm)

    mm.content = "!special 11"
    assert await on_message(mm)

    mm.content = "!special 12"
    assert await on_message(mm)

    mm.content = "!special 30"
    assert await on_message(mm)

    mm.content = "!special 40"
    assert '10-12,30,40' in (await on_message(mm))[0]


@pytest.mark.asyncio
async def test_unspecial():
    mm.content = "!unspecial 11"
    assert (await on_message(mm))[0]


@pytest.mark.asyncio
async def test_stbs():
    mm.content = "!stbs"
    assert '10,12,30,40' in (await on_message(mm))[0]


@pytest.mark.asyncio
async def test_stbp():
    with mock.patch('record_keeper.BOT.client', Client()):
        mm.content = "!stbp 10"
        assert 'bidoof' in (await on_message(mm))[0]


@pytest.mark.asyncio
async def test_stbu():
    with mock.patch('record_keeper.BOT.client', Client()):
        mm.content = "!stbu test"
        assert 'Bidoof' in (await on_message(mm))[0]
