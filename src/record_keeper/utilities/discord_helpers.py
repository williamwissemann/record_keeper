import discord

from record_keeper import BOT


def get_discord_id(raw_msg, search_term):
    identifier = None
    if "<@" in search_term:
        identifier = str(search_term.lstrip("<@!").rstrip(">"))
    else:
        for guild in BOT.client.guilds:
            user = discord.utils.find(
                lambda m: search_term.lower() in m.name.lower()
                or (search_term.lower() in str(m.nick).lower() and m.nick)
                and (raw_msg.guild.id == guild.id),
                guild.members,
            )
            if user:
                identifier = user.id
                break

    if not identifier:
        try:
            int(search_term)
            identifier = search_term
        except Exception:
            return None
    return identifier


def get_discord_name(server, raw_msg, identifier):
    display_name = None
    for guild in BOT.client.guilds:
        if guild.id != server and server != "ViaDirectMessage":
            continue
        for member in guild.members:
            if str(identifier) == str(member.id):
                try:
                    msg_guild_id = raw_msg.guild.id
                except Exception:
                    msg_guild_id = "None"

                if member.nick and msg_guild_id == guild.id:
                    display_name = member.nick.encode("utf8").decode("utf8")
                else:
                    display_name = member.name.encode("utf8").decode("utf8")
                break
        if display_name:
            break
    return display_name