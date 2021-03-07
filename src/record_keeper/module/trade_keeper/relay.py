from typing import Union

from record_keeper.module.admin.query import has_listener
from record_keeper.module.trade_keeper.query import (
    update,
    delete,
    get_by_user,
    get_by_pokemon,
    get_trade_string,

)
from record_keeper.utilities.helpers import (
    force_str_length,
    list_compression,
    resolve_pokemon,
)
from record_keeper.utilities.message import MessageWrapper


class TradeRelay:
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
            elif msg.cmd == "tbs":
                response = self.tbs(msg, board="TRADE_BOARD")
            elif msg.cmd == "tbp":
                response = self.tbp(msg, board="TRADE_BOARD")
            elif msg.cmd == "special":
                response = self.want(msg, board="SPECIAL_TRADE_BOARD")
            elif msg.cmd == "unspecial":
                response = self.unwant(msg, board="SPECIAL_TRADE_BOARD")
            elif msg.cmd == "stbu":
                response = self.tbu(msg, board="SPECIAL_TRADE_BOARD")
            elif msg.cmd == "stbs":
                response = self.tbs(msg, board="SPECIAL_TRADE_BOARD")
            elif msg.cmd == "stbp":
                response = self.tbp(msg, board="SPECIAL_TRADE_BOARD")

        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

        return None

    def want(self, msg: MessageWrapper, board: str = "TRADE_BOARD"):
        try:
            pokemon_name, pokemon_number = resolve_pokemon(msg.arguments[0])
            if not pokemon_name:
                return f"There was an issue adding {msg.arguments[0]}"
        except Exception:
            return "Bidoof, something went wrong, try !help for more info"

        update(
            msg.guild_id,
            pokemon_number,
            pokemon_name,
            str(msg.user.id),
            notes=msg.note,
            board=board,
        )

        bm = f"Added {pokemon_name} ({pokemon_number}) to the {board}!\n"
        bm += self.create_pokemon_trade_table(msg, msg.user.id, board)
        bm += self.create_search_string_table(msg, msg.user.id, board)

        return bm

    def unwant(self, msg, board="TRADE_BOARD"):
        try:
            pokemon_name, pokemon_number = resolve_pokemon(msg.arguments[0])
            if not pokemon_name:
                return f"There was an issue adding {msg.arguments[0]}"
        except Exception:
            return "Bidoof, something went wrong, try !help for more info"

        delete(
            msg.guild_id,
            pokemon_name,
            str(msg.user.id),
            board=board,
        )

        bm = f"Removed {pokemon_name} ({pokemon_number}) to the {board}!"
        return bm

    def tbu(self, msg, board="TRADE_BOARD"):
        user = msg.user.id
        if msg.arguments:
            user = msg.get_discord_id(msg.arguments[0])
            if not user:
                return "Bidoof, cannot find user"

        bm = self.create_pokemon_trade_table(msg, user, board)
        bm += self.create_search_string_table(msg, user, board)
        return bm

    def create_pokemon_trade_table(self, msg, user, board):
        wants = get_by_user(msg.guild_id, user, board)

        if wants:
            msg = (
                f"<@!{user}>'s trade list \n```"
                "Pokemon      |#    |Note   \n"
                "-------------+-----+-------------\n"
            )
            for el in wants:
                pokemon, number, note = el
                if len(note) == 0:
                    continue
                note = force_str_length(note, length=10)
                number = force_str_length(number, length=4)
                msg += f"{pokemon} | {number} | {note} \n"
            msg += "```"
            return msg
        else:
            return f"Bidoof, nothing found for {user}to see here"

    def create_search_string_table(self, msg, user, board):
        trade_string = get_trade_string(msg.guild_id, user, board)

        if len(trade_string) > 0:
            lc = list_compression(trade_string)
            return f"search string: \n```{lc}```"

        return "Bidoof, nothing to see here"

    def tbs(self, msg, board="TRADE_BOARD"):
        user = msg.user.id
        if msg.arguments:
            user = msg.get_discord_id(msg.arguments[0])
            if not user:
                return "Bidoof, cannot find user"

        trade_string = get_trade_string(msg.guild_id, user, board)

        if len(trade_string) > 0:
            return list_compression(trade_string)

        return "Bidoof, nothing to see here"

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

    def create_per_pokemon_trade_table(server, usdb, pokemon, message, board):

        list = get_trade_board_by_pokemon(server, pokemon, board)
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