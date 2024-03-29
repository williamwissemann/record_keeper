from typing import Union

from record_keeper import BOT
from record_keeper.module.admin.query import has_listener
from record_keeper.utilities.message import MessageWrapper


class TrainingWheels:
    """Catch relay class to respond with an error on bad input."""

    async def relay(
        self,
        msg: MessageWrapper,
    ) -> Union[str, None]:
        """Relay logic for when to respond."""
        response = None
        delete_after = 120

        active = has_listener(msg.guild_id, msg.channel_id, "training-wheels")
        if (active or msg.direct_message) and msg.cmd:
            response = BOT.HELP_PROMPT

        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

        return None
