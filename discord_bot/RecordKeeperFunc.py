from Storage import UserStats
from RecordKeeperUtils import get_discord_id

import RecordKeeperViews as bot_message

import discord
import asyncio
import random
import datetime
import math
import time
import sys
import os
import re


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
        try:
            offset = int(message["args"][0])
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

    def find_table_name(self, name):
        for accepted in self.usdb.accepted_tables:
            if accepted.lower() == name.lower():
                return accepted
        for accepted in self.usdb.pvp_leagues:
            if accepted.lower() == name.lower():
                return accepted
        return None

    def up(self, message):
        if 'user' in message:
            identifier = get_discord_id(message, message['user'])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        try:
            medal = self.find_table_name(message["args"][0])
            value = message["args"][1]
            value = value.replace(",", "")
            note = message['note'] if 'note' in message else ""
        except:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if medal not in self.usdb.accepted_tables:
            return "Bidoof, " + message["args"][0] + " can not be found"

        try:
            uuid = self.usdb.update_medal(medal, str(identifier), value, message["date"], note)
        except:
            return "Bidoof, " + value + " can not be found"

        if str(identifier) != str(message["raw_msg"].author.id):
            bm = "<@!" + str(identifier) + "> stats were updated by " + "<@!" + str(message["raw_msg"].author.id) + ">"
            return bm
        else:
            bm = bot_message.create_recent5(self.usdb, medal, str(identifier))
            bm += bot_message.create_stats(self.usdb, medal, str(identifier))
            return bm

    def ls(self, message):
        try:
            medal = self.find_table_name(message["args"][0])
        except:
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
            bm = bot_message.create_recent_pvp10(self.usdb, message, medal, identifier)
            if "Bidoof" not in bm:
                bm += bot_message.create_stats(self.usdb, medal, identifier)
        else:
            bm = bot_message.create_recent5(self.usdb, medal, identifier)
            if "Bidoof" not in bm:
                bm += bot_message.create_stats(self.usdb, medal, identifier)
        return bm

    def uuid(self, message):
        try:
            medal = self.find_table_name(message["args"][0])
        except:
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
            bm = bot_message.create_uuid_table_pvp(self.usdb, message, medal, identifier)
        else:
            bm = bot_message.create_uuid_table(self.usdb, medal, identifier)
        return bm

    def lb(self, message):
        try:
            medal = self.find_table_name(message["args"][0])
        except:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not (medal in self.usdb.accepted_tables or medal in self.usdb.pvp_leagues):
            return "There was an issue listing the stat for " + message["args"][0]

        if medal in self.usdb.pvp_leagues:
            bm = bot_message.create_elo10(self.usdb, medal, message)
        else:
            bm = bot_message.create_leaderboard10(self.usdb, medal, message)
        return bm

    def delete(self, message):
        if 'user' in message:
            identifier = get_discord_id(message, message['user'])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        try:
            medal = self.find_table_name(message["args"][0])
            value = message["args"][1]
            value = value.replace(",", "")
        except:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not medal:
            return "Bidoof, " + message["args"][0] + " can not be found"

        self.usdb.delete_row(medal, identifier, value)
        if medal in self.usdb.pvp_leagues:
            bm = bot_message.create_recent_pvp10(self.usdb, message, medal, identifier)
        else:
            bm = bot_message.create_recent5(self.usdb, medal, identifier)
        return bm

    def add_player(self, message):
        try:
            player = message["args"][0]
            if not self.usdb.gamertag_exists(player):
                self.usdb.add_gamertag(player)
                return "player " + player + " added"
            else:
                return "player " + player + " already added"
        except:
                return "Bidoof, sorry, something went wrong, try !help for more info"

    def pvp(self, message):
        try:
            medal = self.find_table_name(message["args"][0])
            note = message['note'] if 'note' in message else ""

            if medal not in self.usdb.pvp_leagues:
                return "Bidoof, " + message["args"][0] + " can not be found"

            if 't' in message:
                winner = get_discord_id(message, message['t'])
                if len(message["args"]) > 1:
                    search_term = message["args"][1]
                    loser = get_discord_id(message, search_term)
                else:
                    loser = message["raw_msg"].author.id
                try:
                    assert loser and winner and not str(loser) == str(winner)
                except:
                    return "You can't beat yourself"

                self.usdb.update_pvp(
                    medal, message["raw_msg"].author.id,
                    winner, loser, message["date"], 1, note)
            else:
                if 'w' in message:
                    winner = get_discord_id(message, message['w'])
                else:
                    winner = message["raw_msg"].author.id
                if 'l' in message:
                    loser = get_discord_id(message, message['l'])
                else:
                    loser = message["raw_msg"].author.id
                try:
                    assert loser and winner and not str(loser) == str(winner)
                except:
                    return "You can't beat yourself"

                self.usdb.update_pvp(
                    medal, message["raw_msg"].author.id,
                    winner, loser, message["date"], 0, note)
        except:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if medal in self.usdb.pvp_leagues:
            bm = bot_message.create_recent_pvp10(self.usdb, message, medal, winner)
            bm += bot_message.create_stats(self.usdb, medal, winner)
        else:
            return "Bidoof, sorry, something went wrong, try !help for more info"
        return bm

    def want(self, message):
        try:
            note = message['note'] if 'note' in message else ""
        except:
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
        except:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not PokemonName:
            return "There was an issue adding " + message["args"][0]

        self.usdb.update_trade_board(PokemonNumber, PokemonName, str(message["raw_msg"].author.id), note)
        bm = "Added " + PokemonName + " (" + PokemonNumber + ") to the trade board!"
        bm += bot_message.create_pokemon_trade_table(self.usdb, str(message["raw_msg"].author.id))
        bm += bot_message.create_search_string_table(self.usdb, str(message["raw_msg"].author.id))
        return bm

    def unwant(self, message):
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
        except:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not PokemonName:
            return "There was an issue removing " + message["args"][0]

        self.usdb.delete_from_trade_board(PokemonName, str(message["raw_msg"].author.id))
        bm = "Removed " + PokemonName + " (" + PokemonNumber + ") from the trade board!"
        return bm

    def tbu(self, message):
        if len(message["args"]) > 0:
            search_term = message["args"][0]
            identifier = get_discord_id(message, search_term)
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        bm = bot_message.create_pokemon_trade_table(self.usdb, identifier)
        if "Bidoof" not in bm:
            bm += bot_message.create_search_string_table(self.usdb, identifier)
        return bm

    def tbs(self, message):
        if len(message["args"]) > 0:
            identifier = get_discord_id(message, message["args"][0])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        bm = bot_message.create_search_string(self.usdb, identifier)
        return bm

    def tbp(self, message):
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
        except:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not PokemonName:
            return "There was an issue finding " + message["args"][0]

        bm = bot_message.create_per_pokemon_trade_table(self.usdb, PokemonName, message)
        return bm

    def addfriend(self, message):
        if len(message["args"]) > 0:
            identifier = get_discord_id(message, message["args"][0])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        author = message["raw_msg"].author.id
        if identifier == author:
            return "can't add yourself as a friend"
        self.usdb.update_friend_board(identifier, author)
        self.usdb.update_friend_board(author, identifier)
        return "<@!" + str(author) + ">" + ", <@!" + str(identifier) + "> was added to your ultra friend list!"

    def removefriend(self, message):
        if len(message["args"]) > 0:
            identifier = get_discord_id(message, message["args"][0])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        author = message["raw_msg"].author.id
        if identifier == author:
            return "can't add yourself as a friend"
        self.usdb.delete_from_friend_board(identifier, author)
        self.usdb.delete_from_friend_board(author, identifier)
        return "<@!" + str(author) + ">" + ", <@!" + str(identifier) + "> was removed to your ultra friend list!"

    def list_friends(self, message):
        if len(message["args"]) > 0:
            identifier = get_discord_id(message, message["args"][0])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        rm = bot_message.create_friends_table(self.usdb, message, identifier)
        return rm

    def ping_friends(self, message):
        if len(message["args"]) > 0:
            identifier = get_discord_id(message, message["args"][0])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        rm = bot_message.create_ping_table(self.usdb, message, identifier)
        return rm

    def online(self, message):
        author = "<@!" + str(message["raw_msg"].author.id) + ">"
        self.usdb.update_active_board(message["raw_msg"].author.id, "Online")
        return author + " you are now online & accepting invites! (ง'̀-'́)ง"

    def offline(self, message):
        author = "<@!" + str(message["raw_msg"].author.id) + ">"
        self.usdb.update_active_board(message["raw_msg"].author.id, "Offline")
        return author + " you are now offline & no longer accepting invites"

    def rank(self, message):
        try:
            int(message["args"][0])
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
            message["args"][0] = PokemonName
        except:
            pass

        try:
            if len(message["args"]) > 3:
                bm = bot_message.create_rank_header(message)
                bm += bot_message.create_rank_table(message)
                bm += bot_message.create_rank_top10_table(message)
                return bm
            else:
                bm = bot_message.create_rank_header(message)
                bm += bot_message.create_rank_top10_table(message)
                return bm
        except:
            return "Bidoof, something went wrong, double check your IVs"
