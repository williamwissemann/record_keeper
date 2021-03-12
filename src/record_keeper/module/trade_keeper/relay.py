from typing import Union

from record_keeper.module.admin.query import has_listener
from record_keeper.module.trade_keeper.query import (
    delete,
    get_by_pokemon,
    get_by_user,
    get_trade_string,
    update,
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
            elif msg.cmd == "tts":
                response = self.tts(msg, board="TRADE_BOARD")
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
            return BOT.HELP_PROMPT

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
        search_str = self.create_search_string_table(msg, msg.user.id, board)
        if search_str:
            bm += search_str
        return bm

    def unwant(self, msg, board="TRADE_BOARD"):
        try:
            pokemon_name, pokemon_number = resolve_pokemon(msg.arguments[0])
            if not pokemon_name:
                return f"There was an issue adding {msg.arguments[0]}"
        except Exception:
            return BOT.HELP_PROMPT

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
        search_str = self.create_search_string_table(msg, user, board)
        if search_str:
            bm += search_str
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
                pokemon = force_str_length(pokemon, length=12)
                note = force_str_length(note, length=10)
                number = force_str_length(number, length=3)
                msg += f"{pokemon} | {number} | {note} \n"
            msg += "```"
            return msg
        else:
            return f"Bidoof, nothing found for {user} to see here"

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

    def tts(self, msg, board="TRADE_BOARD"):
        user = msg.user.id
        if msg.arguments:
            user = msg.get_discord_id(msg.arguments[0])
            if not user:
                return "Bidoof, cannot find user"

        trade_string = get_trade_string(msg.guild_id, None, board)

        if len(trade_string) > 0:
            trash = [(el,) for el in range(1, 2000)]
            for num in trade_string:
                trash.remove(num)
            return list_compression(trash)

        return "Bidoof, nothing to see here"

    def tbp(self, msg, board="TRADE_BOARD"):
        try:
            pokemon_name, pokemon_number = resolve_pokemon(msg.arguments[0])
            if not pokemon_name:
                return f"There was an issue adding {msg.arguments[0]}"
        except Exception:
            return BOT.HELP_PROMPT

        bm = self.create_per_pokemon_trade_table(msg, pokemon_name, board)
        return bm

    def create_per_pokemon_trade_table(self, msg, pokemon, board):
        wants = get_by_pokemon(msg.guild_id, pokemon, board)
        if wants:
            bm = "```"
            bm += "Want         |Note\n"
            bm += "-------------+-------------\n"
            for el in wants:
                user, note = el

                discord_name = msg.get_discord_name(user)
                discord_name = discord_name.split("#")[0]
                discord_name = force_str_length(discord_name, length=12)

                note = force_str_length(note, length=12)

                bm += f"{discord_name} | {note} \n"
            bm += "```"
            return bm
        else:
            return "Bidoof, nothing to see here"
