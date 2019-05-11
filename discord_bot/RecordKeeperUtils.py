import re
import datetime

def message_parser(message):
    msg = {}
    if re.findall('^![^ ]', message):
        msg['cmd'] = re.findall('^!([^ ]+)', message)[0]
        message = re.sub('^![^ ]+', '', message)
    else:
        return None

    special = re.findall('\w*:[^ ]+', message)
    for s in special:
        key, value = s.split(":")
        if key not in value:
            msg[key.lower()] = value
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
