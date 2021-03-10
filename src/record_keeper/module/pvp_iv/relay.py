from typing import Union

from record_keeper import BOT
from record_keeper.module.admin.query import has_listener
from record_keeper.module.pvp_iv.query import find_combo, find_top_5, get_csv_header
from record_keeper.utilities.helpers import force_str_length, resolve_pokemon
from record_keeper.utilities.message import MessageWrapper


class IVRelay:
    def __init__(self):
        pass

    async def relay(
        self,
        msg: MessageWrapper,
    ) -> Union[str, None]:

        response = None
        delete_after = 120

        active = has_listener(msg.guild_id, msg.channel_id, "iv-ranker")
        if active or msg.direct_message:
            if msg.cmd in ["rankgreat", "rank", "rankg"]:
                response = self.rank(msg, "great")
            if msg.cmd in ["rankultra", "ranku"]:
                response = self.rank(msg, "ultra")
            if msg.cmd in ["rankmaster", "rankm"]:
                response = self.rank(msg, "great")

        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

        return None

    def rank(self, msg, league):
        try:
            pokemon_name, pokemon_number = resolve_pokemon(msg.arguments[0])
            if msg.arguments[0].isdigit():
                msg.arguments[0] = pokemon_name
            else:
                pokemon_name = msg.arguments[0]
        except Exception:
            return BOT.HELP_PROMPT

        try:
            if len(msg.arguments) > 3:
                bm = self.create_rank_header(msg, league)
                bm += self.create_rank_table(msg, league)
                bm += self.create_rank_top5table(msg, league)
                return bm
            else:
                bm = self.create_rank_header(msg, league)
                bm += self.create_rank_top5table(msg, league)
                return bm
        except Exception:
            return "Bidoof, something went wrong, double check your IVs"

    def create_rank_header(self, msg, league):
        if len(msg.arguments) == 5:
            folder = msg.arguments[4]
        elif len(msg.arguments) == 2:
            folder = msg.arguments[1].lower()
        else:
            folder = "wild"

        header_slug = get_csv_header(msg.arguments[0].lower(), folder, league)

        return f"{header_slug} filtered by *{folder}*  in *{league}*\n"

    def create_rank_table(self, msg, league):
        if len(msg.arguments) == 5:
            folder = msg.arguments[4]
        else:
            folder = "wild"

        result, perfect = find_combo(
            msg.arguments[0].lower(),
            msg.arguments[1],
            msg.arguments[2],
            msg.arguments[3],
            folder,
            league,
        )
        result = result.replace("\r\n", " ").split(",")
        perfect = perfect.replace("\r\n", " ").split(",")

        outstring = "```"
        outstring += "RANK:  " + result[0] + " (" + result[11] + ")\n"
        outstring += "CP:    " + result[5] + "\n"

        diff = str(round(float(result[6]) - float(perfect[6]), 2))
        outstring += f"LVL:   {result[6]}  ({diff})  \n"

        diff = str(round(float(result[7]) - float(perfect[7]), 2))
        outstring += f"ATK:   {result[7]}  ({diff})  \n"

        diff = str(round(float(result[8]) - float(perfect[8]), 2))
        outstring += f"DEF:   {result[8]}  ({diff})  \n"

        diff = str(round(float(result[9]) - float(perfect[9]), 2))
        outstring += f"HP:   {result[9]}  ({diff})"

        outstring += "```"
        return outstring

    def create_rank_top5table(self, msg, league):
        if len(msg.arguments) == 5:
            folder = msg.arguments[4]
        elif len(msg.arguments) == 2:
            folder = msg.arguments[1].lower()
        else:
            folder = "wild"

        bm = "```"
        bm += " |ATK|DEF|HP |CP   |LVL  \n"
        bm += "-+---+---+---+-----+-----\n"
        for line in find_top_5(msg.arguments[0].lower(), folder, league):
            row = line.split(",")

            rank = row[0]
            atk = row[1]
            defs = row[2]
            hp = row[3]
            cp = row[5]
            lvl = row[6]

            atk = force_str_length(atk, length=3)
            defs = force_str_length(defs, length=3)
            hp = force_str_length(hp, length=3)
            cp = force_str_length(cp, length=5)

            bm += f"{rank}|{atk}|{defs}|{hp}|{cp}|{lvl}\n"
        bm += "```"
        return bm
