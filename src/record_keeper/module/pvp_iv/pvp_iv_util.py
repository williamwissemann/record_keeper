import gzip
import os
import shutil


def find_combo(pokemon, ATK_IV, DEF_IV, HP_IV, folder, league):
    os.chdir(os.path.abspath(__file__).replace("pvp_iv_util.py", ""))
    path = "./compressed_iv_data/%s/%s/" % (league, folder)
    items = os.listdir(path)
    for files in items:
        if pokemon.lower() == files.replace(".csv.gz", "").lower():
            infile = path + files
            perfect = ""
            cnt = 0
            with gzip.open(infile, "rb") as f:
                for line in f.readlines()[1:]:
                    line = line.decode()
                    if cnt == 1:
                        perfect = line
                    try:
                        (
                            rank,
                            ATK,
                            DEF,
                            HP,
                            IV_P,
                            CP,
                            LVL,
                            ref_ATK,
                            ref_DEF,
                            ref_HP,
                            SP,
                            P,
                        ) = line.split(",")
                    except Exception:
                        continue
                    if ATK == ATK_IV and DEF == DEF_IV and HP == HP_IV:
                        return (line.replace("\r\n", ""), perfect)
                    cnt += 1


def find_top_5(pokemon, folder, league):
    os.chdir(os.path.abspath(__file__).replace("pvp_iv_util.py", ""))
    path = "./compressed_iv_data/%s/%s/" % (league, folder)
    items = os.listdir(path)
    for files in items:
        if pokemon.lower() == files.replace(".csv.gz", "").lower():
            infile = path + files
            print(path)
            array = []
            with gzip.open(infile, "rb") as f:
                for line in f.readlines()[2:7]:
                    line = line.decode().replace("\r\n", "")
                    array.append(line)
                return array


def get_csv_header(pokemon, folder, league):
    os.chdir(os.path.abspath(__file__).replace("pvp_iv_util.py", ""))
    path = "./compressed_iv_data/%s/%s/" % (league, folder)
    items = os.listdir(path)
    for files in items:
        if pokemon.lower() == files.replace(".csv.gz", "").lower():
            infile = path + files
            print(path)
            with gzip.open(infile, "rb") as f:
                for line in f.readlines()[0:2]:
                    line = str(line).split(",")
                    pokemonNum = str(line[0])
                    pokemon = str(line[1])
                    output = (
                        pokemon + "(" + pokemonNum.replace("b'", "").lstrip("0") + ")"
                    )
                    return output
