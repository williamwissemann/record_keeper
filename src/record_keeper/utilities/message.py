import datetime
import re


def parser(message: str) -> dict:
    """Message parser, for discord commands which start with `!`.

    Args:
        message (str): a command starting with !

    Raises:
        ValueError: spacing issue or

    Returns:
        dict: {'cmd': <!command>, 'note': <a note>, 'date': <data>,
        'args': an array of command arguments}
    """
    msg = {}
    if re.findall("^![^ ]", message):
        msg["cmd"] = re.findall("^!([^ ]+)", message)[0]
        message = re.sub("^![^ ]+", "", message)
        msg["cmd"] = msg["cmd"].lower()
    else:
        return None

    # find special annotations of the form word:value
    special = re.findall(r"\w*:\s?[^ ]+", message)
    for s in special:
        try:
            key, value = s.split(":")
        except Exception:
            raise ValueError("malformed command")
        if key not in value:
            msg[key.lower()] = value.lstrip(" ")
        message = re.sub(s, "", message)

    # parse remaining arguments now that the annotations have ben removed
    msg["args"] = re.findall("([^ ]+)", message)

    # converts data into a datetime value
    if "date" in msg and "-" in msg["date"]:
        try:
            year, month, day = msg["date"].split("-")
            date_str = datetime.datetime(int(year), int(month), int(day))
            msg["date"] = str(date_str.isoformat(" "))
        except Exception:
            raise ValueError("not an accepted date format")
    else:
        msg["date"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return msg
