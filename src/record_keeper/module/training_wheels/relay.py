from typing import Union

from record_keeper.module.admin.query import has_listener
from record_keeper.utilities.message import MessageWrapper


class TrainingWheels:
    async def relay(
        self,
        msg: MessageWrapper,
    ) -> Union[str, None]:

        response = None
        delete_after = 120

        active = has_listener(msg.guild_id, msg.channel_id, "training-wheels")
        if active or msg.direct_message:
            response = "Bidoof, something went wrong, try !help for more info"

        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

        return None
