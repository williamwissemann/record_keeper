from record_keeper import STORAGE
from record_keeper import BOT

def list_to_list(in_list: list) -> str:
    in_list = str(sorted(in_list))

    for char in ["[", "]", "'"]:
        in_list = in_list.replace(char, "")

    return in_list


def chunk_message(new, existing, response):
    if len(new) + len(existing) <= 2000:
        existing += new
    else:
        response.append(existing)
        existing = new

    return (existing, response)


def find_table_name(name):
    for accepted in STORAGE.accepted_tables:
        if accepted.lower() == name.lower():
            return accepted
    return None


def get_medal(msg):
    medal = find_table_name(msg.arguments[0])
    if medal not in STORAGE.accepted_tables:
        return None
    return medal


def clean_date_string(date):
    date = str(date)
    date = date.split(".")[0]
    date = date.split(" ")[0]
    return date.split("T")[0]


def force_str_length(string, length):
    string = str(string)
    while len(string) < length:
        string += " "
    return string[0:length]
