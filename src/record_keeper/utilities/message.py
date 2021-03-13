import datetime
import re
from typing import Union

import discord

from record_keeper import BOT
from record_keeper.module.admin.query import has_listener


class BadCommand(Exception):
    """Raised if a command is not useable."""
    pass


class MessageWrapper:
    """Wraps a discord.py message."""
    def __init__(self, message):
        """Initializes using a discord.py message object."""
        self.failure = None
        self.raw_msg = message
        self.cmd = None

        if not self.in_scope:
            return

        self.channel = self.raw_msg.channel
        self.channel_id = str(self.raw_msg.channel.id)
        self.direct_message = False

        self.guild = self.raw_msg.guild
        self.guild_id = None
        self.user = self.raw_msg.author
        self.permissions = None
        self.from_admin = None
        self.can_delete = False
        self.find_by_slug = None
        self.note = None

        if self.guild:
            self.guild_id = str(self.guild.id)
            permissions = self.channel.permissions_for(self.guild.me)
            self.can_manage_messages = permissions.manage_messages
            guild_permissions = self.raw_msg.author.guild_permissions
            self.from_admin = guild_permissions.administrator
        else:
            self.guild_id = "ViaDirectMessage"
            self.direct_message = True

        self.date = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.annotations = {}
        self.arguments = []
        self.response_sent = False

        try:
            self.__parse_message__
            self.__grab_annotations__
            self.__apply_aliases__
        except BadCommand as err:
            self.failure = str(err)

    @property
    def in_scope(self) -> bool:
        """Checks is the message is one the bot can see"""
        if self.raw_msg.author.bot:
            return False

        in_testing_channel = "-testing" in str(self.raw_msg.channel)
        if BOT.environment in ["development", "testing"]:
            return True
        elif BOT.environment == "production" and not in_testing_channel:
            return True
        return False

    @property
    def __parse_message__(self) -> None:
        """Converts a message to a useable command."""
        content = self.raw_msg.content
        if not re.findall("^![^ ]", content):
            return

        self.cmd = re.findall("^!([^ ]+)", content)[0]
        self.cmd = self.cmd.lower()
        self.note = ""

        content = re.sub("^![^ ]+", "", content)
        # find special annotation of the form word:value
        special = re.findall(r"\w*:\s?[^ ]+", content)
        for s in special:
            try:
                key, value = s.split(":")
            except Exception:
                raise BadCommand("Malformed command failed validation.")
            if key not in value:
                self.annotations[key.lower()] = value.lstrip(" ")
            content = re.sub(s, "", content)

        # converts data into a datetime value
        if "-" in self.annotations.get("date", []):
            try:
                year, month, day = self.annotations.get("date").split("-")
                date_str = datetime.datetime(int(year), int(month), int(day))
                self.date = str(date_str.isoformat(" "))
                self.date = self.date.replace(" ", "T")
                del self.annotations["date"]
            except Exception:
                raise BadCommand("Date format failed validation.")

        # parse remaining arguments now that the annotations have been removed
        self.arguments = re.findall("([^ ]+)", content)
        self.arguments = [text.lower() for text in self.arguments]

    @property
    def __grab_annotations__(self) -> None:
        """Parse any annotations on the end of the command."""
        self.note = self.annotations.get("note", "")
        if "note" in self.annotations:
            del self.annotations["note"]

        self.find_by_slug = self.annotations.get("user")
        if "user" in self.annotations:
            del self.annotations["user"]

    @property
    def __apply_aliases__(self) -> None:
        """Applies aliases to commands."""
        if self.arguments:
            aliases = [
                ("mmr", "gblelo"),
                ("fisher", "fisherman"),
                ("railstaff", "depotagent"),
            ]
            for current, alias in aliases:
                if self.arguments[0] == current:
                    self.arguments[0] = alias

    async def send_message(
        self,
        message: Union[str, list],
        delete_after: Union[int, None] = None,
        new_message: bool = False,
    ) -> list:
        """Sends a message back to a discord channel."""
        msg_list = message
        if not isinstance(msg_list, list):
            msg_list = [msg_list]

        # does the channel have cleanup active?
        cleanup_active = has_listener(
            self.guild_id,
            self.channel_id,
            "message-cleanup",
        )

        if not cleanup_active or not self.can_manage_messages:
            delete_after = None

        if cleanup_active and self.can_manage_messages:
            await self.raw_msg.delete()

        for msg in msg_list:
            if new_message:
                bot_msg = await self.channel.send("updating...")
                await bot_msg.edit(content=msg, delete_after=delete_after)
            else:
                await self.channel.send(content=msg, delete_after=delete_after)

        self.response_sent = True

        return msg_list

    def get_discord_id(self, search_term):
        """Finds a discord id based on partical string."""
        if "<@" in search_term:
            return str(search_term.lstrip("<@!").rstrip(">"))
        else:
            for guild in BOT.client.guilds:

                user = discord.utils.find(
                    lambda m: search_term.lower() in m.name.lower()
                    or (search_term.lower() in str(m.nick).lower() and m.nick)
                    and (self.guild_id == guild.id),
                    guild.members,
                )
                if user:
                    return user.id

        return None

    def get_discord_name(self, member_id: str) -> str:
        """Finds the discord name (or nickname) based on discord id."""
        display_name = None
        for guild in BOT.client.guilds:
            if str(guild.id) != self.guild_id and not self.direct_message:
                continue
            for member in guild.members:
                if str(member_id) == str(member.id):
                    if member.nick and self.guild_id == guild.id:
                        display_name = member.nick
                    else:
                        display_name = member.name
            if display_name:
                break
        if display_name:
            return display_name.encode("utf8").decode("utf8")
        else:
            return "bidoof"
