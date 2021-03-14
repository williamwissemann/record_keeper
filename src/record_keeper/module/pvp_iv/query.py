import gzip
import os


def find_combo(pokemon, atk_iv, def_iv, hp_iv, folder, league):
    path = os.path.abspath(__file__).replace("query.py", "")
    path = os.path.join(path, "compressed_iv_data", league, folder)
    items = os.listdir(path)
    for files in items:
        if pokemon.lower() == files.replace(".csv.gz", "").lower():
            in_file = os.path.join(path, files)
            perfect = ""
            cnt = 0
            with gzip.open(in_file, "rb") as f:
                for line in f.readlines()[1:]:
                    line = line.decode()
                    if cnt == 1:
                        perfect = line
                    try:
                        (
                            rank,
                            atk,
                            defs,
                            hp,
                            iv_p,
                            cp,
                            lvl,
                            ref_atk,
                            ref_defs,
                            ref_hp,
                            sp,
                            p,
                        ) = line.split(",")
                    except Exception:  # noqa: S112
                        continue

                    if atk == atk_iv and defs == def_iv and hp == hp_iv:
                        return (line.replace("\r\n", ""), perfect)
                    cnt += 1
    return None


def find_top_5(pokemon, folder, league):
    path = os.path.abspath(__file__).replace("query.py", "")
    path = os.path.join(path, "compressed_iv_data", league, folder)
    items = os.listdir(path)
    for files in items:
        if pokemon.lower() == files.replace(".csv.gz", "").lower():
            infile = os.path.join(path, files)
            array = []
            with gzip.open(infile, "rb") as f:
                for line in f.readlines()[2:7]:
                    line = line.decode().replace("\r\n", "")
                    array.append(line)
                return array
    return None


def get_csv_header(pokemon, folder, league):
    path = os.path.abspath(__file__).replace("query.py", "")
    path = os.path.join(path, "compressed_iv_data", league, folder)
    items = os.listdir(path)
    for files in items:
        if pokemon.lower() == files.replace(".csv.gz", "").lower():
            infile = os.path.join(path, files)
            with gzip.open(infile, "rb") as f:
                for line in f.readlines()[0:2]:
                    line = str(line).split(",")
                    pokemon_num = str(line[0]).replace("b'", "").lstrip("0")
                    pokemon = str(line[1])
                    output = f"{pokemon} ({str(pokemon_num)})"
                    return output.lower()
    return None
