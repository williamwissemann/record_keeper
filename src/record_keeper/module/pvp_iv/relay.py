from typing import Union

from record_keeper.module.admin.query import has_listener
from record_keeper.utilities.message import MessageWrapper


class RecordRelay:
    def __init__(self):
        pass

    async def relay(
        self,
        msg: MessageWrapper,
    ) -> Union[str, None]:

        response = None
        delete_after = 120

        active = has_listener(msg.guild_id, msg.channel_id, "dice")
        if active or msg.direct_message:

        ## XXX ????
        """ def rank(self, message, league):
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


        (
        cmd_msg["cmd"].lower() == "rankgreat"
        or cmd_msg["cmd"].lower() == "rank"
        or cmd_msg["cmd"].lower() == "rankg"
        )
        and BOT.keeper.has_listener(cmd_msg, "iv-ranker")
        and (
        str(BOT.client.user.id) == "588364227396239361"
        or str(BOT.client.user.id) == "491321676835848203"
        )
        ):
        view = BOT.keeper.rank(cmd_msg, "great")
        await send_message(view, direct_message, cmd_msg, 120)
        elif (
        (
        cmd_msg["cmd"].lower() == "rankultra"
        or cmd_msg["cmd"].lower() == "ranku"
        )
        and BOT.keeper.has_listener(cmd_msg, "iv-ranker")
        and (
        str(BOT.client.user.id) == "588364227396239361"
        or str(BOT.client.user.id) == "491321676835848203"
        )
        ):
        view = BOT.keeper.rank(cmd_msg, "ultra")
        await send_message(view, direct_message, cmd_msg, 120)
        elif (
        (
        cmd_msg["cmd"].lower() == "rankmaster"
        or cmd_msg["cmd"].lower() == "rankm"
        )
        and BOT.keeper.has_listener(cmd_msg, "iv-ranker")
        and (
        str(BOT.client.user.id) == "588364227396239361"
        or str(BOT.client.user.id) == "491321676835848203"
        )
        ):
        view = BOT.keeper.rank(cmd_msg, "master")
        await send_message(view, direct_message, cmd_msg, 120)
        """

        ## XXX ???

        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

        return None

def create_rank_header(message, league):
    if len(message["args"]) == 5:
        folder = message["args"][4]
    elif len(message["args"]) == 2:
        folder = message["args"][1].lower()
    else:
        folder = "wild"
    return "%s filtered by *%s*  in *%s*\n" % (
        str(get_csv_header(message["args"][0], folder, league)),
        folder,
        league,
    )


def create_rank_table(message, league):
    if len(message["args"]) == 5:
        folder = message["args"][4]
    else:
        folder = "wild"
    result, perfect = find_combo(
        message["args"][0],
        message["args"][1],
        message["args"][2],
        message["args"][3],
        folder,
        league,
    )
    result = result.replace("\r\n", " ").split(",")
    perfect = perfect.replace("\r\n", " ").split(",")

    outstring = "```"
    outstring += "RANK:  " + result[0] + " (" + result[11] + ")\n"
    outstring += "CP:    " + result[5] + "\n"
    outstring += (
        "LVL:   "
        + result[6]
        + "  ("
        + str(round(float(result[6]) - float(perfect[6]), 2))
        + ") \n"
    )
    outstring += (
        "ATK:   "
        + result[7]
        + " ("
        + str(round(float(result[7]) - float(perfect[7]), 2))
        + ") \n"
    )
    outstring += (
        "DEF:   "
        + result[8]
        + " ("
        + str(round(float(result[8]) - float(perfect[8]), 2))
        + ") \n"
    )
    outstring += (
        "HP:    "
        + result[9]
        + " ("
        + str(round(float(result[9]) - float(perfect[9]), 2))
        + ")```"
    )

    return outstring


def create_rank_top10_table(message, league):
    if len(message["args"]) == 5:
        folder = message["args"][4]
    elif len(message["args"]) == 2:
        folder = message["args"][1].lower()
    else:
        folder = "wild"
    msg = "```"
    msg += " |ATK|DEF|HP |CP   |LVL  \n"
    msg += "-+---+---+---+-----+-----\n"
    for line in find_top_5(message["args"][0], folder, league):
        rank, ATK, DEF, HP, IV_P, CP, LVL, ref_ATK, ref_DEF, ref_HP, SP, P = line.split(
            ","
        )
        while len(ATK) < 2:
            ATK = " " + ATK
        while len(DEF) < 2:
            DEF = " " + DEF
        while len(HP) < 2:
            HP = " " + HP
        while len(CP) < 4:
            CP += " "
        msg += (
            rank
            + "|"
            + str(ATK)
            + " |"
            + str(DEF)
            + " |"
            + str(HP)
            + " |"
            + str(CP)
            + " |"
            + str(LVL)
            + "\n"
        )
    msg += "```"
    return msg
