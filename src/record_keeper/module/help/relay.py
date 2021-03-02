from typing import Union

from record_keeper import STORAGE
from record_keeper.module.admin.query import has_listener
from record_keeper.utilities.helpers import chunk_message, list_to_list
from record_keeper.utilities.message import MessageWrapper


class HelpRelay:
    def __init__(self):
        pass

    async def relay(
        self,
        msg: MessageWrapper,
    ) -> Union[str, None]:

        response = None
        delete_after = 120

        listening = has_listener(msg.guild_id, msg.channel_id, "help")
        if listening or msg.direct_message:
            if msg.cmd == "help":
                response = self.help_prompt(msg)
            elif msg.cmd == "medals":
                response = self.medals_prompt()

        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

        return None

    def help_prompt(self, msg):
        response = []
        bot_msg = (
            "__**COMMAND LIST**__\n"
            "DM the bot !help for a completed list of supported commands\n"
            "---------------------------------------------\n"
        )
        active = has_listener(msg.guild_id, msg.channel_id, "record-keeper")
        if active or msg.direct_message:
            bot_msg, response = chunk_message(
                self.record_prompt(),
                bot_msg,
                response,
            )

        active = has_listener(msg.guild_id, msg.channel_id, "deletable-data")
        if active or msg.direct_message:
            bot_msg, response = chunk_message(
                self.delete_prompt(),
                bot_msg,
                response,
            )

        active = has_listener(msg.guild_id, msg.channel_id, "trade-keeper")
        if active or msg.direct_message:
            bot_msg, response = chunk_message(
                self.trade_prompt(),
                bot_msg,
                response,
            )

        active = has_listener(msg.guild_id, msg.channel_id, "iv-ranker")
        if active or msg.direct_message:
            bot_msg, response = chunk_message(
                self.iv_prompt(),
                bot_msg,
                response,
            )

        response.append(bot_msg)

        return response

    def record_prompt(self):
        return (
            "__**RECORD KEEPER**__\n"
            "_**Update a given medal**_\n"
            "\t!up <*medal*> <*value*>\n"
            "\t!up <*medal*> <*value*> note:<*ExampleNote*>\n"
            "\t**WARNING**: a note can't contain spaces\n"
            "_**List the medal stats for a specific user**_\n"
            "\t!ls <*medal*>\n"
            "\t!ls <*medal*> <*discord_id*>\n"
            "_**List the leaderboards for a given medal**_\n"
            "\t!lb <*medal*>\n"
            "_**View a list of tracked medals**_\n"
            "\t!medals\n"
            "---------------------------------------------\n"
        )

    def medals_prompt(self):
        return (
            "__**Medal Names:**__\n"
            "Basics:"
            f"```{list_to_list(STORAGE.basic_tables)}```"
            "Badges:"
            f"```{list_to_list(STORAGE.badge_tables)}```"
            "Types:"
            f"```{list_to_list(STORAGE.type_tables)}```"
            "Custom Badges:"
            f"```{list_to_list(STORAGE.custom_tables)}```"
        )

    def delete_prompt(self):
        return (
            "__**DELETING**__\n"
            "_**Delete entry via UUID**_\n"
            "\t!del <*medal*> <*uuid*>\n"
            "_**List the UUIDs for a given medal**_\n"
            "\t!uuid <*medal*>\n"
            "**NOTE:** Only entries made in the last 24 hours can be deleted\n"
            "---------------------------------------------\n"
        )

    def trade_prompt(self):
        return (
            "__**TRADE-BOARD**__\n"
            "_**Add a pokémon to the trade board**_\n"
            "\t!want <*pokémon*>\n"
            "\t!want <*pokémon*> note:<*ExampleNote*>\n"
            "\t!want <*dex number*> note:<*ExampleNote*>\n"
            "_**Remove a pokémon from the trade board**_\n"
            "\t!unwant <*pokémon*>\n"
            "\t!unwant <*dex#*>\n"
            "_**List trade board for a pokémon**_\n"
            "\t!tbp <*pokémon or dex number*>\n"
            "_**List a user's trade preferences**_\n"
            "\t!tbu <*discord_id*>\n"
            "_**Prints a copyable version of a users search string**_\n"
            "\t!tbs <*discord_id*>\n"
            "---------------------------------------------\n"
            "__**SPECIAL-TRADE-BOARD**__\n"
            "_**Add a pokémon to the trade board**_\n"
            "\t!special <*pokémon*>\n"
            "\t!special <*pokémon*> note:<*ExampleNote*>\n"
            "\t!special <*dex number*> note:<*ExampleNote*>\n"
            "_**Remove a pokémon from the trade board**_\n"
            "\t!unspecial <*pokémon*>\n"
            "\t!unspecial <*dex#*>\n"
            "_**List trade board for a pokémon**_\n"
            "\t!stbp <*pokémon or dex number*>\n"
            "_**List a user's trade preferences**_\n"
            "\t!stbu <*discord_id*>\n"
            "_**Prints a copyable version of a users search string**_\n"
            "\t!stbs <*discord_id*>\n"
            "---------------------------------------------\n"
        )

    def iv_prompt(self):
        return (
            "__**IV-RANKER**__\n"
            "_**Rank a pokemon for great league**_\n"
            "\t!rankgreat <*pokemon*> <ATK> <DEF> <HP> <filter>\n"
            "\t!rankg <*dex#*> <ATK> <DEF> <HP> <filter>\n"
            "_**Rank a pokemon for great ultra**_\n"
            "\t!rankultra <*pokemon*> <ATK> <DEF> <HP> <filter>\n"
            "\t!ranku <*dex#*> <ATK> <DEF> <HP> <filter>\n"
            "_**Rank a pokemon for great master**_\n"
            "\t!rankmaster <*pokemon*> <ATK> <DEF> <HP> <filter>\n"
            "\t!rankm <*dex#*> <ATK> <DEF> <HP> <filter>\n"
            "**FILTERS:** wild (default), wb (weather boosted),\n"
            "\tbest (best-friends), raid, lucky \n"
            "---------------------------------------------\n"
        )
