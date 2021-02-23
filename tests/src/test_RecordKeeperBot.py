from record_keeper.RecordKeeperBot import on_message
import pytest
import mock
import logging


class mock_guild_permissions():
    def __init__(self):
        self.administrator = True


class mock_author():
    def __init__(self):
        self.name = "111111111111"
        self.bot = False
        self.guild_permissions = mock_guild_permissions()


class mock_message():
    def __init__(self):
        self.author = mock_author()


class mock_bot_setup():
    def __init__(self):
        FORMAT = "%(levelname)s %(filename)s:%(lineno)d %(message)s"
        logging.basicConfig(format=FORMAT)
        logging.root.level = logging.INFO

        self.environment = "development"

@pytest.mark.asyncio
async def test___init__():
    with mock.patch('record_keeper.bot.setup.BotSetup', mock_bot_setup):

        mock_discord_message = mock_message()
        mock_discord_message.channel = "fake-message-testing"
        mock_discord_message.content = "!roll"

        mock_discord_message.author.bot = False

        await on_message(mock_discord_message)

        assert False
