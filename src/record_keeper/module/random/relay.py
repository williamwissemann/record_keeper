import asyncio
import random
from typing import Union

from record_keeper import BOT
from record_keeper.module.admin.query import has_listener
from record_keeper.utilities.message import MessageWrapper


class RandomRelay:
    def __init__(self):
        self.sys_random = random.SystemRandom()

    async def relay(
        self,
        msg: MessageWrapper,
    ) -> Union[str, None]:

        response = None
        delete_after = 120

        active = has_listener(msg.guild_id, msg.channel_id, "dice")
        if active or msg.direct_message:

            if msg.cmd == "d20":
                response = self.roll(msg, 20)
                await asyncio.sleep(3)
            if msg.cmd == "roll":
                if msg.arguments and msg.arguments[0].isdigit():
                    response = self.roll(msg, int(msg.arguments[0]))
                else:
                    response = self.roll(msg)
                await asyncio.sleep(3)

        if msg.cmd == "ping":
            response = f"pong in ({round(BOT.client.latency, 2)})"

        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

        return None

    def roll(self, msg: MessageWrapper, max_value: int = 6) -> str:
        """Rolls a max_value sided die.

        Args:
            msg (MessageWrapper): A wrapped discord.py message object.
            max_value (int, optional): The max the die can roll. Defaults to 6.

        Returns:
            str: The response message
        """
        value = self.sys_random.randint(1, max_value)

        return f"{msg.raw_msg.author.name} rolled a {value} on a d{max_value}"
