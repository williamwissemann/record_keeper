from record_keeper import BOT, STORAGE


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


def resolve_pokemon(pokemon_info: str) -> tuple:
    pokemon_name = None
    pokemon_number = None
    for idx in STORAGE.pokemonByNumber:
        if idx.lower() == pokemon_info:
            pokemon_number = idx
            pokemon_name = STORAGE.pokemonByNumber[idx]
            break
    for idx in STORAGE.pokemonByName:
        if idx.lower() == pokemon_info.lower():
            pokemon_name = idx
            pokemon_number = STORAGE.pokemonByName[idx]
            break
    return (pokemon_name, pokemon_number)


def list_compression(list_to_compress: str) -> tuple:
    array = []
    search = ""
    current = -1
    streak = False

    for el in list_to_compress:
        num = el[0]
        if current + 1 == num:
            current = num
            streak = True
        else:
            if streak:
                streak = False
                search += "-" + str(array[len(array) - 1])
            if len(search) == 0:
                search += str(num)
            else:
                search += "," + str(num)
            current = num
        array.append(num)
    if streak:
        search += "-" + str(array[len(array) - 1])

    return search
