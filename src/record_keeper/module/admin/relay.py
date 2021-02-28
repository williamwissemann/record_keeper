from typing import Union

from record_keeper.module.admin.query import (
    get_listeners,
    remove_listener,
    update_listener,
)
from record_keeper.utilities.message import MessageWrapper


class AdminRelay:
    def __init__(self):

        self.admin_options = [
            "dice",
            "help",
            "battle-keeper",
            "record-keeper",
            "trade-keeper",
            "friend-keeper",
            "iv-ranker",
            "message-cleanup",
            "training-wheels",
            "deletable-data",
        ]

    async def relay(
        self,
        msg: MessageWrapper,
    ) -> Union[str, None]:

        if not msg.guild or not msg.from_admin:
            # incorrect scope or permission do not continue
            return None

        response = None
        delete_after = 120
        # help prompts
        if msg.cmd == "setup":
            response = self.setup()
            delete_after = 600
        # supported commands
        elif msg.cmd == "activate" and msg.arguments:
            response = self.activate(msg)
        elif msg.cmd == "deactivate":
            response = self.deactivate(msg)
        elif msg.cmd == "active":
            response = self.list_listener(msg)
        # send the response to discord
        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

    def setup(self):
        # TODO remove unsupported things
        return (
            "__**Setup**__\n"
            "*run these commands in channels you would like to modify*\n"
            "_**Add a listener to channel**_\n"
            "\t!activate <*listener*>\n"
            "_**Remove a listener from a channel**_\n"
            "\t!deactivate  <*listener*>\n"
            "_**View all listener for a channel**_\n"
            "\t!active\n"
            "_**available listeners**_\n"
            " - **help**: activates !help\n"
            " - **training-wheels**: activates errors on bad commands\n"
            " - **record-keeper**: a record keeper for medals\n"
            " - **trade-keeper**: a trading want manager\n"
            " - **iv-ranker**: a pokemon rater\n"
            " - **message-cleanup**: cleans up bot messages on a timer\n"
            " - **deletable-data**: activates ability to delete\n"
            " - **dice**: activates !roll <*sides*>\n"
            "**Note**: it is recommend to turn on *message-cleanup*, "
            "*training-wheels* and *help* \n"
            "in addition to any other listener (via `!activate default`)\n"
            "---------------------------------------------\n"
        )

    def activate(self, msg: MessageWrapper) -> str:
        settings = []
        if msg.arguments == "all":
            settings = self.admin_options
        elif msg.arguments == "default":
            settings = ["help", "message-cleanup", "training-wheels"]
        else:
            settings.extend(msg.arguments)

        for setting in settings:
            if setting in self.admin_options:
                update_listener(msg.guild_id, msg.channel_id, setting.lower())

        return "Valid listener's status have activated for this channel!"

    def deactivate(self, msg: MessageWrapper) -> str:
        settings = []
        settings.extend(msg.arguments)

        for setting in settings:
            if setting in self.admin_options:
                remove_listener(msg.guild_id, msg.channel_id, setting.lower())

        return "Valid listener's status have deactivated for this channel!"

    def list_listener(self, msg: MessageWrapper) -> str:
        response = (
            "```active listeners on this channel \n\n"
            "channel            | type \n"
            "-------------------+------------\n"
        )
        listeners = get_listeners(msg.guild_id, msg.channel_id)
        for (uuid, server, toggle, channel) in listeners:
            response += f"{channel} | {toggle} \n"
        response += "```"

        return response
