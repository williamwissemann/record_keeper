from Storage import UserStats

import RecordKeeperViews as bot_message

import discord
import asyncio
import random
import datetime
import math
import time
import sys
import os


class RecordKeeper:
    def __init__(self, database_name):
        self.usdb = UserStats(database_name)

    def help(self):
        msg = "---__**Command List**__---\n"
        msg += "__**TRADE BOARD**__\n"
        msg += "_**Add a pokmeon to the trade board**_\n"
        msg += "\t!want <*pokemon name*>\n"
        msg += "\t!want <*pokemon name*> note:<*ExampleNote*>\n"
        msg += "\t!want <*dex number*> note:<*ExampleNote*>\n"
        msg += "_**Remove a pokemon from the trade board**_\n"
        msg += "\t!unwant <*pokemon name*>\n"
        msg += "\t!unwant <*dex number*>\n"
        msg += "_**List trade board for a pokemon**_\n"
        msg += "\t!tbp <*pokemon or dex number*>\n"
        msg += "_**List a user's want list**_\n"
        msg += "\t!tbu <*gamertag*>\n"
        msg += "_**Print a copyable version of the search string**_\n"
        msg += "\t!tbs <*gamertag*>\n"
        msg += "\n"
        msg += "__**PVP**__\n"
        msg += "These commands will log a win/loss for \n"
        msg += "both you and your opponent\n"
        msg += "\t**to log a win**\n"
        msg += "\t!pvp <*pvp league*> L:<*opponents gamertag*>\n"
        msg += "\t**to log a loss**\n"
        msg += "\t!pvp <*pvp league*> W:<*opponents gamertag*>\n"
        msg += "\t**other commands**\n"
        msg += "\tsee !ls and !lb below\n"
        msg += "\n"
        msg += "__**LEADERBOARD**__\n"
        msg += "_**Update a given medal**_\n"
        msg += "\t!up <*medal_name*> <*value*>\n"
        msg += "\t!up <*medal_name*> <*value*> note:<*ExampleNote*>\n"
        msg += "_**List the medal stats for a spacific user**_\n"
        msg += "\t!ls <*medal_name*>\n"
        msg += "\t!ls <*medal_name*> <*gamertag*>\n"
        msg += "_**List the leaderboards for a given medal**_\n"
        msg += "\t!lb <*medal_name*>\n"
        msg += "_**List the uuids for a given medal**_\n"
        msg += "\t!uuid <*medal_name*>\n"
        msg += "_**Delete a entry from a table**_\n"
        msg += "\t!del <*medal_name*> <*uuid*>\n"
        msg += "\n"
        msg += "__**MEDAL NAMES**__\n"
        msg += "_**To get a list of medals**_\n"
        msg += "\t!medals \n"
        msg += "_**To get a list of raid bosses**_\n"
        msg += "\t!raid"
        if (len(msg) >= 2000):
            return "ERROR: message too long"
        return msg

    def medals(self):
        msg = "__**Medal Names:**__\n"
        msg += "Basics:"
        msg += "```"
        msg += str(sorted(self.usdb.basic_tables)).replace("[", "").replace("]", "").replace("'", "")
        msg += "```"
        msg += "Badges:"
        msg += "```"
        msg += str(sorted(self.usdb.badge_tables)).replace("[", "").replace("]", "").replace("'", "")
        msg += "```"
        msg += "Types:"
        msg += "```"
        msg += str(sorted(self.usdb.type_tables)).replace("[", "").replace("]", "").replace("'", "")
        msg += "```"
        msg += "JP badges:"
        msg += "```"
        msg += str(sorted(self.usdb.custom_tables)).replace("[", "").replace("]", "").replace("'", "")
        msg += "```"
        msg += "Raids:"
        msg += "```"
        msg += "use !raid to get a list of all the raid bosses"
        msg += "```"
        if (len(msg) >= 2000):
            return "ERROR: message too long"
        return msg

    def raid(self, message):
        entry_per = (15 * 4)
        max_pages = str(math.ceil(len(self.usdb.raid_tables) / (entry_per)))
        msg = message.content.split()
        try:
            offset = int(msg[1])
        except:
            offset = 1
        if offset > int(max_pages):
            offset = 1

        offset = offset - 1
        list = sorted(self.usdb.raid_tables)[0 + (entry_per * offset): entry_per + (entry_per * offset)]

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
        if (len(msg) >= 2000):
            return "ERROR: message too long"
        return msg

    def stat_message_parse(self, message):
        msg_dic = {}
        msg = message.content.split()
        msg[0] = msg[0].lower()
        try:
            if not (msg[0] == "!pvp" or msg[0] == "!tbu" or msg[0] == "!tbs" or msg[0] == "!tbp"):
                for accepted in self.usdb.accepted_tables:
                    if accepted.lower() == msg[1].lower():
                        msg[1] = accepted
                        break
            if (msg[0] == "!ls" or
                    msg[0] == "!del" or
                    msg[0] == "!lb" or
                    msg[0] == "!uuid" or
                    msg[0] == "!pvp"):
                for accepted in self.usdb.pvp_leagues:
                    if accepted.lower() == msg[1].lower():
                        msg[1] = accepted
                        break
        except:
            raise ValueError("issue matching accepted_tables")
        if msg[0] == "!up" or msg[0] == "!del":
            if len(msg) > 2 and msg[1] in self.usdb.accepted_tables:
                medal = str(msg[1])
            else:
                raise ValueError("There was an issue updating that stat")
            # value to add
            value = str(msg[2])
            for el in msg:
                # user to update
                if "user:" in el:
                    user = el.replace("user:", "")
                else:
                    user = message.author
                # parse the note
                if "note:" in el:
                    note = el.replace("note:", "")
                else:
                    note = ""
                # handles back dating a stat
                if "date:" in el and "-" in el:
                    try:
                        y, m, d = el.replace("date:", "").split("-")
                        date = str(datetime.datetime(int(y), int(m), int(d)).isoformat(' '))
                    except:
                        raise ValueError("not an accepted date format")
                else:
                    date = datetime.datetime.now().isoformat()
            return {"medal": medal, "value": value, "user": user, "date": date, "note": note}
        elif msg[0] == "!ls" or msg[0] == "!uuid" or msg[0] == "!lb":
            if (len(msg) > 1 and (msg[1] in self.usdb.accepted_tables or msg[1] in self.usdb.pvp_leagues)):
                medal = str(msg[1])
            else:
                raise ValueError("There was an issue listing the stat")
            if len(msg) < 3:
                user = message.author
            elif len(msg) >= 3:
                user = discord.utils.find(lambda m: msg[2].lower() in m.name.lower(), message.server.members)
                if user is None:
                    if self.usdb.gamertag_exists(msg[2]):
                        user = msg[2]
            return {"medal": medal, "user": user}
        elif msg[0] == "!pvp":
            if (len(msg) > 2 and
                msg[1] in self.usdb.pvp_leagues and
                ("w:" in message.content.lower() or
                 "l:" in message.content.lower())):
                medal = str(msg[1])
                user = message.author
                date = datetime.datetime.now().isoformat()
                note = ""
                loser = None
                winner = None
                for el in msg:
                    el = el.replace("W:", "w:")
                    el = el.replace("L:", "l:")
                    if "w:" in el.lower():
                        winner = el.replace("w:", "")
                        winner = discord.utils.find(lambda m: winner.lower() in m.name.lower(), message.server.members)
                        if winner is None:
                            if not self.usdb.gamertag_exists(el.replace("w:", "")):
                                raise ValueError("There was an issue listing the stat")
                            else:
                                winner = str(el.replace("w:", ""))

                    if "l:" in el.lower():
                        loser = el.replace("l:", "")
                        loser = discord.utils.find(lambda m: loser.lower() in m.name.lower(), message.server.members)
                        if loser is None:
                            if not self.usdb.gamertag_exists(el.replace("l:", "")):
                                raise ValueError("There was an issue listing the stat")
                            else:
                                loser = str(el.replace("l:", ""))

                    if "note:" in el:
                        note = el.replace("note:", "")
                if loser is None:
                    loser = user
                if winner is None:
                    winner = user
                if loser == winner:
                    raise ValueError("loser == winner")
                return {"medal": medal, "user": user, "winner": winner, "loser": loser, "date": date, "note": note}
        elif msg[0] == "!want" or msg[0] == "!unwant" or msg[0] == "!tbp":
            try:
                for x in self.usdb.pokemonByNumber:
                    if x.lower() == msg[1].lower():
                        PokemonNumber = x
                        PokemonName = self.usdb.pokemonByNumber[x]
                        msg[1] = PokemonName
                        break
                for x in self.usdb.pokemonByName:
                    if x.lower() == msg[1].lower():
                        PokemonName = x
                        PokemonNumber = self.usdb.pokemonByName[x]
                        msg[1] = PokemonName
                        break
            except:
                raise ValueError("There was an issue listing the stat")
            if (len(msg) > 1 and msg[1] in self.usdb.pokemonByName):
                user = message.author
                note = ""
                for el in msg:
                    if "note:" in el:
                        note = el.replace("note:", "")
                return {"PokemonNumber": PokemonNumber, "PokemonName": PokemonName, "user": user, "note": note}
        elif msg[0] == "!tbu" or "!tbs":
            if len(msg) <= 1:
                user = message.author
            elif len(msg) > 1:
                user = discord.utils.find(lambda m: msg[1].lower() in m.name.lower(), message.server.members)
            print(user)
            return {"user": user}
        elif msg[0] == "!tbp":
            if len(msg) <= 1:
                user = message.author
            elif len(msg) > 1:
                user = discord.utils.find(lambda m: msg[1].lower() in m.name.lower(), message.server.members)
            return {"user": user}

    def up(self, message):
        try:
            msg_dict = self.stat_message_parse(message)
        except ValueError as err:
            # XXX: phase 2 add error handling
            print(err.args)
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not self.usdb.gamertag_exists(str(msg_dict["user"])):
            # XXX: phase 2 add "did you mean?"
            return "user not found"

        uuid = self.usdb.update_medal(
            msg_dict["medal"],
            msg_dict["user"],
            msg_dict["value"],
            msg_dict["date"],
            msg_dict["note"])

        if msg_dict["user"] != message.author:
            bm = user + " stats were updated by " + str(message.author)
            return bm
        else:
            bm = bot_message.create_recent5(self.usdb, msg_dict["medal"], msg_dict["user"])
            bm += bot_message.create_stats(self.usdb, msg_dict["medal"], msg_dict["user"])
            return bm

    def ls(self, message):
        try:
            msg_dict = self.stat_message_parse(message)
        except ValueError as err:
            # XXX: phase 2 add error handling
            print(err.args)
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if msg_dict["medal"] in self.usdb.pvp_leagues:
            bm = bot_message.create_recent_pvp10(self.usdb, msg_dict["medal"], msg_dict["user"])
            bm += bot_message.create_stats(self.usdb, msg_dict["medal"], msg_dict["user"])
        else:
            bm = bot_message.create_recent5(self.usdb, msg_dict["medal"], msg_dict["user"])
            bm += bot_message.create_stats(self.usdb, msg_dict["medal"], msg_dict["user"])
        return bm

    def uuid(self, message):
        try:
            msg_dict = self.stat_message_parse(message)
        except ValueError as err:
            # XXX: phase 2 add error handling
            print(err.args)
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if msg_dict["medal"] in self.usdb.pvp_leagues:
            bm = bot_message.create_uuid_table_pvp(self.usdb, msg_dict["medal"], msg_dict["user"])
        else:
            bm = bot_message.create_uuid_table(self.usdb, msg_dict["medal"], msg_dict["user"])
        return bm

    def lb(self, message):
        try:
            msg_dict = self.stat_message_parse(message)
        except ValueError as err:
            # XXX: phase 2 add error handling
            print(err.args)
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if msg_dict["medal"] in self.usdb.pvp_leagues:
            bm = bot_message.create_elo10(self.usdb, msg_dict["medal"])
        else:
            bm = bot_message.create_leaderboard10(self.usdb, msg_dict["medal"])
        return bm

    def delete(self, message):
        try:
            msg_dict = self.stat_message_parse(message)
        except ValueError as err:
            # XXX: phase 2 add error handling
            print(err.args)
            return "Bidoof, sorry, something went wrong, try !help for more info"

        self.usdb.delete_row(msg_dict["medal"], msg_dict["user"], msg_dict["value"])
        if msg_dict["medal"] in self.usdb.pvp_leagues:
            bm = bot_message.create_recent_pvp10(self.usdb, msg_dict["medal"], msg_dict["user"])
        else:
            bm = bot_message.create_recent5(self.usdb, msg_dict["medal"], msg_dict["user"])
        return bm

    def add_player(self, message):
        try:
            msg = message.content.split()
            if not self.usdb.gamertag_exists(str(msg[1])):
                self.usdb.add_gamertag(str(msg[1]))
                return "player " + msg[1] + " added"
            else:
                return "player " + msg[1] + " already added"
        except:
                return "Bidoof, sorry, something went wrong, try !help for more info"

    def pvp(self, message):
        try:
            msg_dict = self.stat_message_parse(message)
        except ValueError as err:
            # XXX: phase 2 add error handling
            print(err.args)
            return "Bidoof, sorry, something went wrong, try !help for more info"

        self.usdb.update_pvp(
            msg_dict["medal"], msg_dict["user"], msg_dict["winner"],
            msg_dict["loser"], msg_dict['date'], msg_dict["note"])
        if msg_dict["medal"] in self.usdb.pvp_leagues:
            bm = bot_message.create_recent_pvp10(self.usdb, msg_dict["medal"], msg_dict["user"])
            bm += bot_message.create_stats(self.usdb, msg_dict["medal"], msg_dict["user"])
        else:
            return "Bidoof, sorry, something went wrong, try !help for more info"
        return bm

    def want(self, message):
        try:
            msg_dict = self.stat_message_parse(message)
        except ValueError as err:
            # XXX: phase 2 add error handling
            print(err.args)
            return "Bidoof, sorry, something went wrong, try !help for more info"
        self.usdb.update_trade_board(
            msg_dict["PokemonNumber"], msg_dict["PokemonName"], msg_dict["user"], msg_dict["note"])
        bm = "Added " + msg_dict["PokemonNumber"] + " (" + msg_dict["PokemonName"] + ") to the trade board!"
        bm += bot_message.create_pokemon_trade_table(self.usdb, msg_dict["user"])
        bm += bot_message.create_search_string_table(self.usdb, msg_dict["user"])
        return bm

    def unwant(self, message):
        try:
            msg_dict = self.stat_message_parse(message)
        except ValueError as err:
            # XXX: phase 2 add error handling
            print(err.args)
            return "Bidoof, sorry, something went wrong, try !help for more info"
        self.usdb.delete_from_trade_board(msg_dict["PokemonName"], msg_dict["user"])
        bm = "Removed " + msg_dict["PokemonName"] + " (" + msg_dict["PokemonNumber"] + ") from the trade board!"
        return bm

    def tbu(self, message):
        try:
            msg_dict = self.stat_message_parse(message)
        except ValueError as err:
            # XXX: phase 2 add error handling
            print(err.args)
            return "Bidoof, sorry, something went wrong, try !help for more info"
        bm = bot_message.create_pokemon_trade_table(self.usdb, msg_dict["user"])
        bm += bot_message.create_search_string_table(self.usdb, msg_dict["user"])
        return bm

    def tbs(self, message):
        try:
            msg_dict = self.stat_message_parse(message)
        except ValueError as err:
            # XXX: phase 2 add error handling
            print(err.args)
            return "Bidoof, sorry, something went wrong, try !help for more info"
        bm = bot_message.create_search_string(self.usdb, msg_dict["user"])
        return bm

    def tbp(self, message):
        try:
            msg_dict = self.stat_message_parse(message)
        except ValueError as err:
            # XXX: phase 2 add error handling
            print(err.args)
            return "Bidoof, sorry, something went wrong, try !help for more info"
        bm = bot_message.create_per_pokemon_trade_table(self.usdb, msg_dict["PokemonName"])
        return bm
