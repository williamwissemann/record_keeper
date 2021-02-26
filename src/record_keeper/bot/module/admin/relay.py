from record_keeper.bot.module.admin.query import (
    get_listeners,
    remove_listener,
    update_listener,
)


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
        raw_msg: object,
        cmd_msg: dict,
        direct_message: bool = False,
    ) -> str:

        is_admin = raw_msg.author.guild_permissions.administrator
        if direct_message or not is_admin:
            # incorrect scope or permission do not continue
            return None

        if cmd_msg.get("cmd") == "setup":
            response = self.setup()
            await raw_msg.channel.send(response, delete_after=600)
            return response

        elif cmd_msg.get("cmd") == "activate" and len(cmd_msg.get("args")):
            response = self.activate(raw_msg, cmd_msg)
            await raw_msg.channel.send(response, delete_after=60)
            return response

        elif cmd_msg.get("cmd") == "deactivate":
            response = self.deactivate(raw_msg, cmd_msg)
            await raw_msg.channel.send(response, delete_after=60)
            return response

        elif cmd_msg.get("cmd") == "active":
            response = self.list_listener(raw_msg, cmd_msg)
            await raw_msg.channel.send(response, delete_after=90)
            return response

        return None

    def setup(self):
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
            " - **friend-keeper**: an ultra friends for pvp\n"
            " - **battle-keeper**: an elo based leaderboard\n"
            " - **iv-ranker**: a pokemon rater\n"
            " - **message-cleanup**: cleans up bot messages on a timer\n"
            " - **deletable-data**: activates ability to delete\n"
            " - **dice**: activates !roll <*sides*>\n"
            "**Note**: it is recommend to turn on *message-cleanup*, "
            "*training-wheels* and *help* \n"
            "in addition to any other listener (via `!activate default`)\n"
            "---------------------------------------------\n"
        )

    def activate(self, raw_msg: object, cmd_msg: dict) -> str:
        arg = cmd_msg.get("args")[0].lower()

        if arg == "all":
            for setting in self.admin_options:
                update_listener(
                    raw_msg.guild.id,
                    raw_msg.channel.id,
                    setting.lower(),
                )
            return "all valid listener are activated"
        elif arg == "default":
            for setting in ["help", "message-cleanup", "training-wheels"]:
                update_listener(
                    raw_msg.guild.id,
                    raw_msg.channel.id,
                    setting.lower(),
                )
            return "default listeners are activate"
        elif arg not in self.admin_options:
            return f"{arg} not a valid listener"
        else:
            try:
                update_listener(
                    raw_msg.guild.id,
                    raw_msg.channel.id,
                    arg.lower(),
                )
            except Exception:
                return f"{arg} not a valid listener"
            return f"listener ({arg}) was activated for this channel"

    def deactivate(self, raw_msg: object, cmd_msg: dict) -> str:
        arg = cmd_msg.get("args")[0].lower()

        if arg not in self.admin_options:
            return f"{arg} not a valid listener"

        remove_listener(raw_msg.guild.id, raw_msg.channel.id, arg.lower())
        return f"listener ({arg}) removed for this channel"

    def list_listener(self, raw_msg: object, cmd_msg: dict) -> str:
        string = (
            "```active listeners on this channel \n\n"
            "channel            | type \n"
            "-------------------+------------\n"
        )
        listeners = get_listeners(raw_msg.guild.id, raw_msg.channel.id)
        for (uuid, server, toggle, channel) in listeners:
            string += f"{channel} | {toggle} \n"
        string += "```"

        return string

    """
    def has_listener(self, raw_msg: object, cmd_msg: dict, toggle: str) -> str:
        # XXX not sure where to put this
        if "Direct Message" in str(raw_msg.channel):
            return True

        response = has_listeners(raw_msg.guild.id, raw_msg.channel.id, toggle)

        return len(response)
    """
