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
        if (
            cmd_msg["cmd"].lower() == "roll" or cmd_msg["cmd"].lower() == "d20"
        ) and BOT.keeper.has_listener(cmd_msg, "dice"):

            update_message = await message.channel.send("rolling...")
            # dice rolls d6
            await asyncio.sleep(2)
            if len(cmd_msg["args"]) > 0:
                counter = random.randint(1, int(cmd_msg["args"][0]))
            elif cmd_msg["cmd"].lower() == "d20":
                counter = random.randint(1, 20)
            else:
                counter = random.randint(1, 6)
            bot_msg = "{} rolled a {}".format(message.author.name, counter)
            await update_message.edit(content=bot_msg)
        ## XXX ???

        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

        return None
