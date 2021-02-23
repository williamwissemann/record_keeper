import asyncio
import datetime
import math
import os
import random
import re
import sys
import time

import discord
import RecordKeeperViews as bot_message
from RecordKeeperUtils import get_discord_id
from Storage import UserStats


class RecordKeeper:
    def __init__(self, database_name, version):
        self.usdb = UserStats(database_name, version)

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

    """
    CAT0: ADMIN Functionality
    """

    def activate(self, message):
        if message["args"][0].lower() == "all":
            for setting in self.admin_options:
                self.usdb.update_listener(
                    message["raw_msg"].guild.id,
                    message["raw_msg"].channel.id,
                    setting.lower(),
                )
            return "all valid listener are activated"
        elif message["args"][0].lower() == "default":
            for setting in ["help", "message-cleanup", "training-wheels"]:
                self.usdb.update_listener(
                    message["raw_msg"].guild.id,
                    message["raw_msg"].channel.id,
                    setting.lower(),
                )
            return "default listeners are activate"

        if message["args"][0].lower() not in self.admin_options:
            return "{} not a valid listener".format(message["args"][0])

        try:
            self.usdb.update_listener(
                message["raw_msg"].guild.id,
                message["raw_msg"].channel.id,
                message["args"][0].lower(),
            )
        except Exception:
            pass
        return "listener ({}) was activated for this channel".format(message["args"][0])

    def deactivate(self, message):
        if message["args"][0].lower() not in self.admin_options:
            self.usdb.remove_listener(
                message["raw_msg"].guild.id,
                message["raw_msg"].channel.id,
                message["args"][0].lower(),
            )
            return "{} not a valid listener".format(message["args"][0])
        self.usdb.remove_listener(
            message["raw_msg"].guild.id,
            message["raw_msg"].channel.id,
            message["args"][0].lower(),
        )
        return "listener ({}) removed for this channel".format(message["args"][0])

    def list_listener(self, message):
        string = "```active listeners on this channel \n"
        string += "\n"
        string += "channel            | type \n"
        string += "-------------------+------------\n"
        for (uuid, server, toggle, channel) in self.usdb.get_listeners(
            message["raw_msg"].guild.id, message["raw_msg"].channel.id
        ):
            string += "{} | {}".format(channel, toggle) + "\n"
        string += "```"
        return string

    def has_listener(self, message, toggle):
        if "Direct Message" in str(message["raw_msg"].channel):
            return True
        return (
            len(
                self.usdb.has_listeners(
                    message["raw_msg"].guild.id, message["raw_msg"].channel.id, toggle
                )
            )
            > 0
        )

    def setup(self, user_msg):
        msg = "__**Setup**__\n"
        msg += "*run these commands in channels you would like to modify*\n"
        msg += "_**Add a listener to channel**_\n"
        msg += "\t!activate <*listener*>\n"
        msg += "_**Remove a listener from a channel**_\n"
        msg += "\t!deactivate  <*listener*>\n"
        msg += "_**View all listener for a channel**_\n"
        msg += "\t!active\n"
        msg += "_**available listeners**_\n"
        msg += " - **help**: activiates !help\n"
        msg += " - **training-wheels**: activiates error messages on bad commands\n"
        msg += " - **record-keeper**: a record keeper for medals\n"
        msg += " - **trade-keeper**: a trading want manager\n"
        msg += " - **friend-keeper**: an ultra friends for pvp\n"
        msg += " - **battle-keeper**: an elo based leaderbaord\n"
        if (
            str(user_msg["client"].user.id) == "588364227396239361"
            or str(user_msg["client"].user.id) == "491321676835848203"
        ):
            msg += " - **iv-ranker**: a pokemon rater\n"
        msg += " - **message-cleanup**: cleans up bot messages on a timer\n"
        msg += " - **deletable-data**: activiates commands for delete bad entries\n"
        msg += " - **dice**: activiates !roll <*sides*>\n"
        msg += "**Note**: it is recommend to turn on *message-cleanup*, *training-wheels* and *help* \n"
        msg += "in addition to any other listner (via `!activate default`)\n"
        msg += "---------------------------------------------\n"
        return msg

    def stats(self, user_msg):
        cnt = 0
        for x in user_msg["client"].guilds:
            cnt += 1
        msg = "servers: {} \n".format(cnt)
        members = {}
        for x in user_msg["client"].get_all_members():
            members[x] = None
        for x in user_msg["client"].get_all_members():
            members[x] = None
        msg += "users: {} \n".format(len(members))
        return msg

    def servers(self, user_msg):
        messages = []
        msg = ""
        servers = {}
        for x in user_msg["client"].guilds:
            servers[str(x)] = None
        for x in sorted(servers.keys()):
            if len(msg + str(x) + "\n") > 1900:
                messages.append(msg)
                msg = ""
            msg += str(x) + "\n"
        messages.append(msg)
        return messages

    """
    CAT1: GENERAL Functionality
    """

    def help(self, user_msg):  # noqa: C901
        messages = []
        msg = "__**COMMAND LIST**__\n"
        msg += "DM the bot !help for a completed list of supported commands\n"
        msg += "---------------------------------------------\n"
        if self.has_listener(user_msg, "record-keeper"):
            add_msg = self.helpRecordKeeper()
            if len(add_msg) + len(msg) <= 2000:
                msg += add_msg
            else:
                messages.append(msg)
                msg = add_msg
        if self.has_listener(user_msg, "deletable-data"):
            add_msg = self.helpDeletableData()
            if len(add_msg) + len(msg) <= 2000:
                msg += add_msg
            else:
                messages.append(msg)
                msg = add_msg
        if self.has_listener(user_msg, "friend-keeper"):
            add_msg = self.helpFriendKeeper()
            if len(add_msg) + len(msg) <= 2000:
                msg += add_msg
            else:
                messages.append(msg)
                msg = add_msg
        if self.has_listener(user_msg, "battle-keeper"):
            add_msg = self.helpBattleKeeper()
            if len(add_msg) + len(msg) <= 2000:
                msg += add_msg
            else:
                messages.append(msg)
                msg = add_msg
        if self.has_listener(user_msg, "trade-keeper"):
            add_msg = self.helpTradeKeeper()
            if len(add_msg) + len(msg) <= 2000:
                msg += add_msg
            else:
                messages.append(msg)
                msg = add_msg
        if self.has_listener(user_msg, "iv-ranker") and (
            str(user_msg["client"].user.id) == "588364227396239361"
            or str(user_msg["client"].user.id) == "491321676835848203"
        ):
            add_msg = self.helpIVRanker()
            if len(add_msg) + len(msg) <= 2000:
                msg += add_msg
            else:
                messages.append(msg)
                msg = add_msg
        if "Direct Message" in str(user_msg["raw_msg"].channel):
            add_msg = self.helpDonate()
            if len(add_msg) + len(msg) <= 2000:
                msg += add_msg
            else:
                messages.append(msg)
                msg = add_msg
        messages.append(msg)
        return messages

    def helpRecordKeeper(self):
        msg = "__**RECORD KEEPER**__\n"
        msg += "_**Update a given medal**_\n"
        msg += "\t!up <*medal*> <*value*>\n"
        msg += "\t!up <*medal*> <*value*> note:<*ExampleNote*>\n"
        msg += "\t**WARNING**: a note can't contain spaces\n"
        msg += "_**List the medal stats for a spacific user**_\n"
        msg += "\t!ls <*medal*>\n"
        msg += "\t!ls <*medal*> <*discord_id*>\n"
        msg += "_**List the leaderboards for a given medal**_\n"
        msg += "\t!lb <*medal*>\n"
        msg += "_**View a list of tracked medals**_\n"
        msg += "\t!medals\n"
        msg += "---------------------------------------------\n"
        return msg

    def helpDeletableData(self):
        msg = "__**DELETING**__\n"
        msg += "_**Delete entry via UUID**_\n"
        msg += "\t!del <*medal*> <*uuid*>\n"
        msg += "_**List the UUIDs for a given medal**_\n"
        msg += "\t!uuid <*medal*>\n"
        msg += "**NOTE:** Only entries made in the last 24 hours can be deleted\n"
        msg += "---------------------------------------------\n"
        return msg

    def helpFriendKeeper(self):
        msg = "__**FRIEND-KEEPER**__\n"
        msg += "_**Add a friend**_\n"
        msg += "\t!add-friend <*discord_id*>\n"
        msg += "\t!auf <*discord_id*>\n"
        msg += "_**Remove a friend**_\n"
        msg += "\t!remove-friend <*discord_id*>\n"
        msg += "\t!ruf <*discord_id*>\n"
        msg += "_**List friends**_\n"
        msg += "\t!friends\n"
        msg += "_**Notify friends**_\n"
        msg += "\t!ping-friends <message>\n"
        msg += "\t!ltb <message>\n"
        msg += "_**toggle status**_\n"
        msg += "\t!online\n"
        msg += "\t!offline\n"
        msg += "---------------------------------------------\n"
        return msg

    def helpBattleKeeper(self):
        msg = "__**BATTLE-KEEPER**__\n"
        msg += "These commands will log a win/loss for \n"
        msg += "both you and your opponent\n"
        msg += "**To log a loss**\n"
        msg += "\t!pvp <*league*> L:<*discord_id*>\n"
        msg += "**To log a win**\n"
        msg += "\t!pvp <*league*> W:<*discord_id*>\n"
        msg += "**To log a tie**\n"
        msg += "\t!pvp <*league*> T:<*discord_id*>\n"
        msg += "\t**other commands**\n"
        msg += "_**List the battle logs**_\n"
        msg += "\t!ls <*league*>\n"
        msg += "\t!ls <*league*> <*discord_id*>\n"
        msg += "_**List the elo leaderboard for a league**_\n"
        msg += "\t!lb <*league*>\n"
        msg += "_**View a list of all tracked leagues**_\n"
        msg += "\t!leagues\n"
        msg += "**NOTE:** elo is updated every 4 hours\n"
        msg += "---------------------------------------------\n"
        return msg

    def helpTradeKeeper(self):
        msg = "__**TRADE-BOARD**__\n"
        msg += "_**Add a pokmeon to the trade board**_\n"
        msg += "\t!want <*pokemon*>\n"
        msg += "\t!want <*pokemon*> note:<*ExampleNote*>\n"
        msg += "\t!want <*dex number*> note:<*ExampleNote*>\n"
        msg += "_**Remove a pokemon from the trade board**_\n"
        msg += "\t!unwant <*pokemon*>\n"
        msg += "\t!unwant <*dex#*>\n"
        msg += "_**List trade board for a pokemon**_\n"
        msg += "\t!tbp <*pokemon or dex number*>\n"
        msg += "_**List a user's trade prefrences**_\n"
        msg += "\t!tbu <*discord_id*>\n"
        msg += "_**Prints a copyable version of a users search string**_\n"
        msg += "\t!tbs <*discord_id*>\n"
        msg += "---------------------------------------------\n"
        msg += "__**SPECIAL-TRADE-BOARD**__\n"
        msg += "_**Add a pokmeon to the trade board**_\n"
        msg += "\t!special <*pokemon*>\n"
        msg += "\t!special <*pokemon*> note:<*ExampleNote*>\n"
        msg += "\t!special <*dex number*> note:<*ExampleNote*>\n"
        msg += "_**Remove a pokemon from the trade board**_\n"
        msg += "\t!unspecial <*pokemon*>\n"
        msg += "\t!unspecial <*dex#*>\n"
        msg += "_**List trade board for a pokemon**_\n"
        msg += "\t!stbp <*pokemon or dex number*>\n"
        msg += "_**List a user's trade prefrences**_\n"
        msg += "\t!stbu <*discord_id*>\n"
        msg += "_**Prints a copyable version of a users search string**_\n"
        msg += "\t!stbs <*discord_id*>\n"
        msg += "---------------------------------------------\n"
        return msg

    def helpIVRanker(self):
        msg = "__**IV-RANKER**__\n"
        msg += "_**Rank a pokemon for great league**_\n"
        msg += "\t!rankgreat <*pokemon*> <ATK> <DEF> <HP> <filter>\n"
        msg += "\t!rankg <*dex#*> <ATK> <DEF> <HP> <filter>\n"
        msg += "_**Rank a pokemon for great ultra**_\n"
        msg += "\t!rankultra <*pokemon*> <ATK> <DEF> <HP> <filter>\n"
        msg += "\t!ranku <*dex#*> <ATK> <DEF> <HP> <filter>\n"
        msg += "_**Rank a pokemon for great master**_\n"
        msg += "\t!rankmaster <*pokemon*> <ATK> <DEF> <HP> <filter>\n"
        msg += "\t!rankm <*dex#*> <ATK> <DEF> <HP> <filter>\n"
        msg += "**FILTERS:** wild (default), wb (weather boosted),\n"
        msg += "\tbest (best-friends), raid, lucky \n"
        msg += "---------------------------------------------\n"
        return msg

    def helpDonate(self):
        msg = "__**Donate**__\n"
        msg += "Looking to help support the bot use !donate\n"
        msg += "---------------------------------------------\n"
        return msg

    def helpDonateLink(self):
        msg = "paypal: https://paypal.me/aDyslexicPanda \n"
        msg += "patreon: https://www.patreon.com/gostadium \n"
        msg += "Keep hunting trainers!"
        return msg

    def medals(self):
        msg = "__**Medal Names:**__\n"
        msg += "Basics:"
        msg += "```"
        msg += (
            str(sorted(self.usdb.basic_tables))
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
        )
        msg += "```"
        msg += "Badges:"
        msg += "```"
        msg += (
            str(sorted(self.usdb.badge_tables))
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
        )
        msg += "```"
        msg += "Types:"
        msg += "```"
        msg += (
            str(sorted(self.usdb.type_tables))
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
        )
        msg += "```"
        msg += "Custom Badges:"
        msg += "```"
        msg += (
            str(sorted(self.usdb.custom_tables))
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
        )
        msg += "```"
        msg += "Raids:"
        msg += "```"
        msg += "use !raid to get a list of all the raid bosses"
        msg += "```"
        if len(msg) >= 2000:
            return "ERROR: message too long"
        return msg

    def leagues(self):
        msg = "__**Leauges:**__\n"
        msg += "```"
        msg += (
            str(sorted(self.usdb.pvp_leagues))
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
        )
        msg += "```"
        if len(msg) >= 2000:
            return "ERROR: message too long"
        return msg

    def raid(self, message):
        entry_per = 15 * 4
        max_pages = str(math.ceil(len(self.usdb.raid_tables) / (entry_per)))
        try:
            offset = int(message["args"][0])
        except Exception:
            offset = 1
        if offset > int(max_pages):
            offset = 1

        offset = offset - 1
        start = entry_per * offset
        end = entry_per + (entry_per * offset)
        list = sorted(self.usdb.raid_tables)[start:end]

        msg = "---__**Command List**__---\n"
        if offset == 0:
            msg += "_**Update a given statistics**_\n"
            msg += "\t!up <*medal_name*> <*value*>\n"
            msg += "_**List a given statistics**_\n"
            msg += "\t!ls <*medal_name*>\n"
            msg += "\t!ls <*medal_name*> <*gamertag*>\n"
            msg += "_**List a give leadboard**_\n"
            msg += "\t!lb <*medal_name*>\n"
        msg += "_**Move to next raid boss page**_\n"
        msg += "\t!raid <*page_number*>\n"
        msg += "\n"
        msg += "_**Boss Naming Conventions**_\n"
        msg += "\tA : Alolan, N: Neutral, BB : Boss Boosted, CB : Counter Boosted"
        msg += "\n"
        msg += "__**Bosses:**__"
        msg += "```"
        msg += str(list).replace("[", "").replace("]", "").replace("'", "")
        msg += "```"
        msg += "page " + str(offset + 1) + " of " + max_pages
        if len(msg) >= 2000:
            return "ERROR: message too long"
        return msg

    def find_table_name(self, name):
        for accepted in self.usdb.accepted_tables:
            if accepted.lower() == name.lower():
                return accepted
        for accepted in self.usdb.pvp_leagues:
            if accepted.lower() == name.lower():
                return accepted
        return None

    def up(self, message):  # noqa: C901
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        if "user" in message:
            identifier = get_discord_id(message, message["user"])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        try:
            medal = self.find_table_name(message["args"][0])
            value = message["args"][1]
            value = value.replace(",", "")
            note = message["note"] if "note" in message else ""
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if medal not in self.usdb.accepted_tables:
            return "Bidoof, " + message["args"][0] + " can not be found"

        try:
            self.usdb.update_medal(
                server, medal, str(identifier), value, message["date"], note
            )
        except Exception:
            return "Bidoof, " + value + " can not be found"

        if str(identifier) != str(message["raw_msg"].author.id):
            bm = (
                "<@!"
                + str(identifier)
                + "> stats were updated by "
                + "<@!"
                + str(message["raw_msg"].author.id)
                + ">"
            )
            return bm
        else:
            bm = bot_message.create_recent5(server, self.usdb, medal, str(identifier))
            bm += bot_message.create_stats(server, self.usdb, medal, str(identifier))
            return bm

    def ls(self, message):  # noqa: C901
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        try:
            medal = self.find_table_name(message["args"][0])
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"
        if len(message["args"]) > 1:
            search_term = message["args"][1]
            identifier = get_discord_id(message, search_term)
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        if not (medal in self.usdb.accepted_tables or medal in self.usdb.pvp_leagues):
            return "There was an issue listing the stat for " + message["args"][0]

        if medal in self.usdb.pvp_leagues:
            bm = bot_message.create_recent_pvp10(
                server, self.usdb, message, medal, identifier
            )
            if "Bidoof" not in bm:
                bm += bot_message.create_stats(
                    server, self.usdb, medal, str(identifier)
                )
        else:
            bm = bot_message.create_recent5(server, self.usdb, medal, identifier)
            if "Bidoof" not in bm:
                bm += bot_message.create_stats(
                    server, self.usdb, medal, str(identifier)
                )
        return bm

    def uuid(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        try:
            medal = self.find_table_name(message["args"][0])
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"
        if len(message["args"]) > 1:
            search_term = message["args"][1]
            identifier = get_discord_id(message, search_term)
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        if not (medal in self.usdb.accepted_tables or medal in self.usdb.pvp_leagues):
            return "There was an issue listing the stat for " + message["args"][0]

        if medal in self.usdb.pvp_leagues:
            bm = bot_message.create_uuid_table_pvp(
                server, self.usdb, message, medal, identifier
            )
        else:
            bm = bot_message.create_uuid_table(server, self.usdb, medal, identifier)
        return bm

    def lb(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        try:
            medal = self.find_table_name(message["args"][0])
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not (medal in self.usdb.accepted_tables or medal in self.usdb.pvp_leagues):
            return "There was an issue listing the stat for " + message["args"][0]

        if medal in self.usdb.pvp_leagues:
            bm = bot_message.create_elo10(server, self.usdb, medal, message)
        else:
            bm = bot_message.create_leaderboard10(server, self.usdb, medal, message)
        return bm

    def delete(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        if "user" in message:
            identifier = get_discord_id(message, message["user"])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        try:
            medal = self.find_table_name(message["args"][0])
            value = message["args"][1]
            value = value.replace(",", "")
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not medal:
            return "Bidoof, " + message["args"][0] + " can not be found"

        self.usdb.delete_row(server, medal, identifier, value)
        if medal in self.usdb.pvp_leagues:
            bm = bot_message.create_recent_pvp10(
                server, self.usdb, message, medal, identifier
            )
        else:
            bm = bot_message.create_recent5(server, self.usdb, medal, identifier)
        return bm

    def add_player(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        try:
            player = message["args"][0]
            if not self.usdb.gamertag_exists(server, player):
                self.usdb.add_gamertag(server, player)
                return "player " + player + " added"
            else:
                return "player " + player + " already added"
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"

    def pvp(self, message):  # noqa: C901
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        try:
            medal = self.find_table_name(message["args"][0])
            note = message["note"] if "note" in message else ""

            if medal not in self.usdb.pvp_leagues:
                return "Bidoof, " + message["args"][0] + " can not be found"

            if "t" in message:
                winner = get_discord_id(message, message["t"])
                if len(message["args"]) > 1:
                    search_term = message["args"][1]
                    loser = get_discord_id(message, search_term)
                else:
                    loser = message["raw_msg"].author.id
                try:
                    assert loser and winner and not str(loser) == str(winner)
                except Exception:
                    return "You can't beat yourself"

                self.usdb.update_pvp(
                    server,
                    medal,
                    message["raw_msg"].author.id,
                    winner,
                    loser,
                    message["date"],
                    1,
                    note,
                )
            else:
                if "w" in message:
                    winner = get_discord_id(message, message["w"])
                else:
                    winner = message["raw_msg"].author.id
                if "l" in message:
                    loser = get_discord_id(message, message["l"])
                else:
                    loser = message["raw_msg"].author.id
                try:
                    assert loser and winner and not str(loser) == str(winner)
                except Exception:
                    return "You can't beat yourself"

                self.usdb.update_pvp(
                    server,
                    medal,
                    message["raw_msg"].author.id,
                    winner,
                    loser,
                    message["date"],
                    0,
                    note,
                )
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if medal in self.usdb.pvp_leagues:
            bm = bot_message.create_recent_pvp10(
                server, self.usdb, message, medal, winner
            )
            bm += bot_message.create_stats(server, self.usdb, medal, winner)
        else:
            return "Bidoof, sorry, somehing went wrong, try !help for more info"
        return bm

    def want(self, message, board="TRADE_BOARD"):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        try:
            note = message["note"] if "note" in message else ""
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        try:
            PokemonName = None
            for x in self.usdb.pokemonByNumber:
                if x.lower() == message["args"][0].lower():
                    PokemonNumber = x
                    PokemonName = self.usdb.pokemonByNumber[x]
                    break
            for x in self.usdb.pokemonByName:
                if x.lower() == message["args"][0].lower():
                    PokemonName = x
                    PokemonNumber = self.usdb.pokemonByName[x]
                    break
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not PokemonName:
            return "There was an issue adding " + message["args"][0]

        self.usdb.update_trade_board(
            server,
            PokemonNumber,
            PokemonName,
            str(message["raw_msg"].author.id),
            notes=note,
            board=board,
        )

        bm = f"Added {PokemonName} ({PokemonNumber}) to the {board}!"
        bm += bot_message.create_pokemon_trade_table(
            server, self.usdb, str(message["raw_msg"].author.id), board
        )
        bm += bot_message.create_search_string_table(
            server, self.usdb, str(message["raw_msg"].author.id), board
        )
        return bm

    def unwant(self, message, board="TRADE_BOARD"):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        try:
            PokemonName = None
            for x in self.usdb.pokemonByNumber:
                if x.lower() == message["args"][0].lower():
                    PokemonNumber = x
                    PokemonName = self.usdb.pokemonByNumber[x]
                    break
            for x in self.usdb.pokemonByName:
                if x.lower() == message["args"][0].lower():
                    PokemonName = x
                    PokemonNumber = self.usdb.pokemonByName[x]
                    break
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not PokemonName:
            return "There was an issue removing " + message["args"][0]

        self.usdb.delete_from_trade_board(
            server, PokemonName, str(message["raw_msg"].author.id), board
        )
        bm = f"Removed {PokemonName} ({PokemonNumber}) to the {board}!"
        return bm

    def tbu(self, message, board="TRADE_BOARD"):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        if len(message["args"]) > 0:
            search_term = message["args"][0]
            identifier = get_discord_id(message, search_term)
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        bm = bot_message.create_pokemon_trade_table(
            server, self.usdb, identifier, board
        )
        if "Bidoof" not in bm:
            bm += bot_message.create_search_string_table(
                server, self.usdb, identifier, board
            )
        return bm

    def tbs(self, message, board="TRADE_BOARD"):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        if len(message["args"]) > 0:
            identifier = get_discord_id(message, message["args"][0])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        bm = bot_message.create_search_string(server, self.usdb, identifier, board)
        return bm

    def tbp(self, message, board="TRADE_BOARD"):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        try:
            PokemonName = None
            for x in self.usdb.pokemonByNumber:
                if x.lower() == message["args"][0].lower():
                    PokemonName = self.usdb.pokemonByNumber[x]
                    break
            for x in self.usdb.pokemonByName:
                if x.lower() == message["args"][0].lower():
                    PokemonName = x
                    break
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not PokemonName:
            return "There was an issue finding " + message["args"][0]

        bm = bot_message.create_per_pokemon_trade_table(
            server, self.usdb, PokemonName, message, board
        )
        return bm

    def addfriend(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        if len(message["args"]) > 0:
            identifier = get_discord_id(message, message["args"][0])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        author = message["raw_msg"].author.id
        if identifier == author:
            return "can't add yourself as a friend"
        self.usdb.update_friend_board(server, identifier, author)
        self.usdb.update_friend_board(server, author, identifier)
        return (
            "<@!"
            + str(author)
            + ">"
            + ", <@!"
            + str(identifier)
            + "> was added to your ultra friend list!"
        )

    def removefriend(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        if len(message["args"]) > 0:
            identifier = get_discord_id(message, message["args"][0])
        if not identifier:
            return "Bidoof, cannot find user"

        author = message["raw_msg"].author.id
        if identifier == author:
            return "can't add yourself as a friend"
        self.usdb.delete_from_friend_board(server, identifier, author)
        self.usdb.delete_from_friend_board(server, author, identifier)
        return (
            "<@!"
            + str(author)
            + ">"
            + ", <@!"
            + str(identifier)
            + "> was removed from your ultra friend list!"
        )

    def list_friends(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        if len(message["args"]) > 0:
            identifier = get_discord_id(message, message["args"][0])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        rm = bot_message.create_friends_table(server, self.usdb, message, identifier)
        return rm

    def ping_friends(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"
        if "user" in message and len(message["user"]) > 0:
            identifier = message["user"]
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        rm = bot_message.create_ping_table(server, self.usdb, message, identifier)
        return rm

    def online(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"
        author = "<@!" + str(message["raw_msg"].author.id) + ">"
        self.usdb.update_active_board(server, message["raw_msg"].author.id, "Online")
        return author + " you are now online & accepting invites! (ง'̀-'́)ง"

    def offline(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        author = "<@!" + str(message["raw_msg"].author.id) + ">"
        self.usdb.update_active_board(server, message["raw_msg"].author.id, "Offline")
        return author + " you are now offline & no longer accepting invites"

    def rank(self, message, league):
        try:
            int(message["args"][0])
            PokemonName = None
            for x in self.usdb.pokemonByNumber:
                if x.lower() == message["args"][0].lower():
                    PokemonName = self.usdb.pokemonByNumber[x]
                    break
            for x in self.usdb.pokemonByName:
                if x.lower() == message["args"][0].lower():
                    PokemonName = x
                    break
            message["args"][0] = PokemonName
        except Exception:
            pass

        try:
            if len(message["args"]) > 3:
                bm = bot_message.create_rank_header(message, league)
                bm += bot_message.create_rank_table(message, league)
                bm += bot_message.create_rank_top10_table(message, league)
                return bm
            else:
                bm = bot_message.create_rank_header(message, league)
                bm += bot_message.create_rank_top10_table(message, league)
                return bm
        except Exception:
            return "Bidoof, something went wrong, double check your IVs"
