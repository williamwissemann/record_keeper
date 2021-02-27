import datetime
import logging
import re
from typing import Union

from record_keeper import BOT
from record_keeper.bot.module.admin.query import has_listener


class BadCommand(Exception):
    pass


class MessageWrapper:
    def __init__(self, message):
        self.failure = None
        self.raw_msg = message

        if not self.in_scope:
            return
        self.channel = self.raw_msg.channel
        self.channel_id = str(self.raw_msg.channel.id)

        self.guild = self.raw_msg.guild
        self.guild_id = None
        self.permissions = None
        self.from_admin = None
        self.can_delete = False

        if self.guild:
            self.guild_id = str(self.guild.id)
            permissions = self.channel.permissions_for(self.guild.me)
            self.can_manage_messages = permissions.manage_messages
            guild_permissions = self.raw_msg.author.guild_permissions
            self.from_admin = guild_permissions.administrator

        self.from_a_bot = message.author.bot

        self.cmd = None
        self.date = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.annotations = {}
        self.arguments = []

        try:
            self.__parse_message__()
        except BadCommand as err:
            self.failure = str(err)

    @property
    def in_scope(self) -> bool:
        in_testing_channel = "-testing" in str(self.raw_msg.channel)
        if BOT.environment == "development":
            return True
        elif BOT.environment == "production" and not in_testing_channel:
            return True
        return False

    def __parse_message__(self) -> None:
        content = self.raw_msg.content
        if not re.findall("^![^ ]", content):
            return

        self.cmd = re.findall("^!([^ ]+)", content)[0]
        self.cmd = self.cmd.lower()

        content = re.sub("^![^ ]+", "", content)
        # find special annotation of the form word:value
        special = re.findall(r"\w*:\s?[^ ]+", content)
        for s in special:
            try:
                key, value = s.split(":")
            except Exception:
                raise BadCommand("Malformed command failed validation.")
            if key not in value:
                self.annotation[key.lower()] = value.lstrip(" ")
            content = re.sub(s, "", content)

        # converts data into a datetime value
        if "-" in self.annotations.get("date", []):
            try:
                year, month, day = self.annotations.get("date").split("-")
                date_str = datetime.datetime(int(year), int(month), int(day))
                self.date = str(date_str.isoformat(" "))
                del self.annotations["date"]
            except Exception:
                raise BadCommand("Date format failed validation.")

        # parse remaining arguments now that the annotations have been removed
        self.arguments = map(str.lower, re.findall("([^ ]+)", content))

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
                await bot_msg.edit(msg, delete_after=delete_after)
            else:
                await self.channel.send(msg, delete_after=delete_after)

        return msg_list
