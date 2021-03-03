from typing import Union

from record_keeper.module.admin.query import has_listener
from record_keeper.utilities.message import MessageWrapper


class RecordRelay:
    async def relay(
        self,
        msg: MessageWrapper,
    ) -> Union[str, None]:

        response = None
        delete_after = 120

        active = has_listener(msg.guild_id, msg.channel_id, "trade-keeper")
        if active or msg.direct_message:

            if msg.cmd == "want":
                response = self.want(msg, board="TRADE_BOARD")
            elif msg.cmd == "unwant":
                response = self.unwant(msg, board="TRADE_BOARD")
            elif msg.cmd == "tbu":
                response = self.tbu(msg, board="TRADE_BOARD")
            elif msg.cmd == "tbp":
                response = self.tbp(msg, board="TRADE_BOARD")
            elif msg.cmd == "special":
                response = self.want(msg, board="SPECIAL_TRADE_BOARD")
            elif msg.cmd == "unspecial":
                response = self.unwant(msg, board="SPECIAL_TRADE_BOARD")
            elif msg.cmd == "stbu":
                response = self.unwant(msg, board="SPECIAL_TRADE_BOARD")
            elif msg.cmd == "stbs":
                response = self.unwant(msg, board="SPECIAL_TRADE_BOARD")
            elif msg.cmd == "stbp":
                response = self.unwant(msg, board="SPECIAL_TRADE_BOARD")

        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

        return None

    def create_search_string(server, usdb, gamertag, board):
        """
        Creates a most recent 5 for a medal, gamertag
        """
        list = usdb.get_trade_board_by_user(server, str(gamertag), board)
        if len(list) > 0:
            msg = ""
            array = []
            search = ""
            current = -1
            streak = False
            for el in list:
                u, s, g, p, num, n = el
                if current + 1 == num:
                    current = num
                    streak = True
                else:
                    if streak:
                        streak = False
                        search += "-" + str(array[len(array) - 1])
                    if len(search) == 0:
                        search += str(num)
                    else:
                        search += "," + str(num)
                    current = num
                array.append(num)
            if streak:
                search += "-" + str(array[len(array) - 1])
            msg += search
            return msg
        else:
            return "Bidoof, nothing to see here"

    def create_search_string_table(server, usdb, gamertag, board):
        """
        Creates a most recent 5 for a medal, gamertag
        """
        list = usdb.get_trade_board_by_user(server, str(gamertag), board)
        if len(list) > 0:
            msg = "search string:\n"
            msg += "```"
            array = []
            search = ""
            current = -1
            streak = False
            for el in list:
                u, s, g, p, num, n = el
                if current + 1 == num:
                    current = num
                    streak = True
                else:
                    if streak:
                        streak = False
                        search += "-" + str(array[len(array) - 1])
                    if len(search) == 0:
                        search += str(num)
                    else:
                        search += "," + str(num)
                    current = num
                array.append(num)
            if streak:
                search += "-" + str(array[len(array) - 1])
            msg += search + "\n"
            msg += "```"
            return msg
        else:
            return "Bidoof, nothing to see here"

    def create_pokemon_trade_table(server, usdb, gamertag, board):
        """
        Creates a most recent 5 for a medal, gamertag
        """
        list = usdb.get_trade_board_by_user(server, str(gamertag), board)
        if len(list) > 0:
            msg = "```"
            msg += "Pokemon      |#    |Note   \n"
            msg += "-------------+-----+-------------\n"
            for el in list:
                u, s, g, p, num, n = el
                p = p[0:12]
                while len(p) < 12:
                    p += " "
                num = str(num)[0:10]
                while len(num) < 4:
                    num += " "
                n = n[0:10]
                if len(n) == 0:
                    continue
                while len(n) < 10:
                    n += " "
                msg += str(p) + " | " + str(num) + "| " + str(n) + "\n"
            msg += "```"
            return msg
        else:
            return "Bidoof, nothing to see here"

    def create_per_pokemon_trade_table(server, usdb, pokemon, message, board):
        """
        Creates a most recent 5 for a medal, gamertag
        """
        list = usdb.get_trade_board_by_pokemon(server, str(pokemon), board)
        if len(list) > 0:
            msg = "```"
            msg += "Want         |Note   \n"
            msg += "-------------+-------------\n"
            for el in list:
                u, s, g, p, num, n = el
                n = n[0:10]
                while len(n) < 12:
                    n += " "
                try:
                    g = get_discord_name(server, message, g)
                    assert g
                except Exception:
                    g = "bidoof"
                g = g.split("#")[0][0:12]
                while len(g) < 12:
                    g += " "
                msg += str(g) + " | " + str(n) + "\n"
            msg += "```"
            return msg
        else:
            return "Bidoof, nothing to see here"

    def want(self, message, board="TRADE_BOARD"):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        try:
            note = message["note"] if "note" in message else ""
        except Exception:
            return "Bidoof, something went wrong, try !help for more info"

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
            return "Bidoof, something went wrong, try !help for more info"

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
            return "Bidoof, something went wrong, try !help for more info"

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
            return "Bidoof, something went wrong, try !help for more info"

        if not PokemonName:
            return "There was an issue finding " + message["args"][0]

        bm = bot_message.create_per_pokemon_trade_table(
            server, self.usdb, PokemonName, message, board
        )
        return bm
