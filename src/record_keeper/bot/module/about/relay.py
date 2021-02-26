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
