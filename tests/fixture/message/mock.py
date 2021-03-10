import mock
import pytest


class MockGuildPermissions:
    def __init__(self):
        pass


class MockGuild:
    def __init__(self):
        pass


class Permissions:
    @property
    def manage_messages(self):
        return True


class MockChannel:
    def __init__(self):
        self.channel_name = "mock-testing"

    def __str__(self):
        return self.channel_name

    def permissions_for(self, *args):
        return Permissions()

    @pytest.mark.asyncio
    async def send(self, *args, **kargs):
        return MockMessage()


class MockAuthor:
    def __init__(self):
        self.guild_permissions = MockGuildPermissions()


class MockMessage:
    def __init__(self):
        self.author = MockAuthor()
        self.author.bot = False
        self.author.id = "mock_author_id"
        self.author.guild_permissions.administrator = True

        self.channel = MockChannel()
        self.channel.id = "mock_channel_id"

        self.guild = MockGuild()
        self.guild.id = "mock_guild_id"
        self.guild.me = "mock_me"

    @pytest.mark.asyncio
    async def edit(self, *args, **kargs):
        return MockMessage()

    @pytest.mark.asyncio
    async def delete(self, *args, **kargs):
        return MockMessage()


"""
class mock_bot_setup():
    def __init__(self):
        FORMAT = "%(levelname)s %(filename)s:%(lineno)d %(message)s"
        logging.basicConfig(format=FORMAT)
        logging.root.level = logging.INFO

        self.environment = "development"

@pytest.mark.asyncio
async def test___init__():
    with mock.patch('record_keeper.setup.BotSetup', mock_bot_setup):

        mock_discord_message = mock_message()
        mock_discord_message.channel = "fake-message-testing"
        mock_discord_message.content = "!roll"
        mock_discord_message.author.bot = False

        try:
            await on_message(mock_discord_message)
        except:
            ''' force pass '''
            pass
"""
