from typing import Union

from record_keeper import BOT
from record_keeper.utilities.message import MessageWrapper


class BotInfo:
    def __init__(self):
        pass

    async def relay(
        self,
        msg: MessageWrapper,
    ) -> Union[str, None]:

        response = None
        delete_after = 120

        if str(msg.raw_msg.author.id) == "204058877317218304":

            if msg.cmd == "stats":
                response = self.stats()

            if msg.cmd == "servers":
                response = self.servers()

        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

        return None

    def stats(self):
        cnt = 0
        for x in BOT.client.guilds:
            cnt += 1
        msg = "servers: {} \n".format(cnt)
        members = {}
        for x in BOT.client.get_all_members():
            members[x] = None
        for x in BOT.client.get_all_members():
            members[x] = None
        msg += f"users: {len(members)} \n"
        return msg

    def servers(self):
        messages = []
        msg = ""
        servers = {}
        for x in BOT.client.guilds:
            servers[str(x)] = None
        for x in sorted(servers.keys()):
            if len(msg + str(x) + "\n") > 1900:
                messages.append(msg)
                msg = ""
            msg += f"{str(x)} \n"
        messages.append(msg)
        return messages
