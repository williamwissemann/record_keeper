"""
elif (
    cmd_msg["cmd"].lower() == "stats"
    and str(cmd_msg["raw_msg"].author.id) == "204058877317218304"
):
    checkpoint_two = False
    view = BOT.keeper.stats(cmd_msg)
    await send_message(view, direct_message, cmd_msg, 300)
elif (
    cmd_msg["cmd"].lower() == "servers"
    and str(cmd_msg["raw_msg"].author.id) == "204058877317218304"
):
    checkpoint_two = False
    view = BOT.keeper.servers(cmd_msg)
    await send_message(view, direct_message, cmd_msg, 300)
"""

# TODO fix this
@BOT.database.get
def get_database_version(self) -> str:
    return "SELECT info FROM botinfo WHERE field = 'version'"


def stats(self, user_msg):
    cnt = 0
    for x in user_msg["client"].guilds:
        cnt += 1
    msg = "servers: {} \n".format(cnt)
    members = {}
    for x in user_msg["client"].get_all_members():
        members[x] = None
    for x in user_msg["client"].get_all_members():
        members[x] = None
    msg += "users: {} \n".format(len(members))
    return msg


def servers(self, user_msg):
    messages = []
    msg = ""
    servers = {}
    for x in user_msg["client"].guilds:
        servers[str(x)] = None
    for x in sorted(servers.keys()):
        if len(msg + str(x) + "\n") > 1900:
            messages.append(msg)
            msg = ""
        msg += str(x) + "\n"
    messages.append(msg)
    return messages
