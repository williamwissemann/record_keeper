import re
import datetime
import discord


def message_parser(message):
    msg = {}
    if re.findall('^![^ ]', message):
        msg['cmd'] = re.findall('^!([^ ]+)', message)[0]
        message = re.sub('^![^ ]+', '', message)
    else:
        return None

    special = re.findall('\w*:\s?[^ ]+', message)
    for s in special:
        try:
            key, value = s.split(":")
        except:
            return "spacing issue"
        if key not in value:
            msg[key.lower()] = value.lstrip(" ")
        message = re.sub(s, '', message)

    msg["args"] = re.findall('([^ ]+)', message)

    if "date" in msg and "-" in msg["date"]:
        try:
            y, m, d = msg["date"].split("-")
            msg["date"] = str(datetime.datetime(int(y), int(m), int(d)).isoformat(' '))
        except:
            raise ValueError("not an accepted date format")
    else:
        msg["date"] = datetime.datetime.now().isoformat()

    return msg


def get_discord_id(message, search_term):
    if '<@' in search_term:
        identifier = str(search_term.lstrip("<@!").rstrip(">"))
    else:
        for guild in message["client"].guilds:
            user = discord.utils.find(lambda m:
                                      search_term.lower() in m.name.lower() or
                                      (search_term.lower() in str(m.nick).lower() and m.nick) and
                                      (message["raw_msg"].guild.id == guild.id),
                                      guild.members)
            if user:
                    identifier = user.id
                    break
    try:
        found = False
        for guild in message["client"].guilds:
            for member in guild.members:
                if int(identifier) == member.id:
                    found = True
                    break
            if found:
                break
        assert found
    except:
        return None

    return identifier


def get_discord_name(message, identifier):
    try:
        found = False
        for guild in message["client"].guilds:
            for member in guild.members:
                try:
                    if str(identifier) == str(member.id):
                        if member.nick and message["raw_msg"].guild.id == guild.id:
                            display_name = member.nick.encode('utf8').decode('utf8')
                        else:
                            display_name = member.name.encode('utf8').decode('utf8')
                        found = True
                        break
                except Exception as e:
                    print(e)

        assert found
    except:
        return None

    return display_name
