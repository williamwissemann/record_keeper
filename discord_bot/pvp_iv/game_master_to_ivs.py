from urllib.request import urlopen
import json
from itertools import product
import numpy as np
import math
import os
import gzip

cp_multiplier = {
    1: 0.094,
    1.5: 0.135137432,
    2: 0.16639787,
    2.5: 0.192650919,
    3: 0.21573247,
    3.5: 0.236572661,
    4: 0.25572005,
    4.5: 0.273530381,
    5: 0.29024988,
    5.5: 0.306057377,
    6: 0.3210876,
    6.5: 0.335445036,
    7: 0.34921268,
    7.5: 0.362457751,
    8: 0.37523559,
    8.5: 0.387592406,
    9: 0.39956728,
    9.5: 0.411193551,
    10: 0.42250001,
    10.5: 0.432926419,
    11: 0.44310755,
    11.5: 0.4530599578,
    12: 0.46279839,
    12.5: 0.472336083,
    13: 0.48168495,
    13.5: 0.4908558,
    14: 0.49985844,
    14.5: 0.508701765,
    15: 0.51739395,
    15.5: 0.525942511,
    16: 0.53435433,
    16.5: 0.542635767,
    17: 0.55079269,
    17.5: 0.558830576,
    18: 0.56675452,
    18.5: 0.574569153,
    19: 0.58227891,
    19.5: 0.589887917,
    20: 0.59740001,
    20.5: 0.604818814,
    21: 0.61215729,
    21.5: 0.619399365,
    22: 0.62656713,
    22.5: 0.633644533,
    23: 0.64065295,
    23.5: 0.647576426,
    24: 0.65443563,
    24.5: 0.661214806,
    25: 0.667934,
    25.5: 0.674577537,
    26: 0.68116492,
    26.5: 0.687680648,
    27: 0.69414365,
    27.5: 0.700538673,
    28: 0.70688421,
    28.5: 0.713164996,
    29: 0.71939909,
    29.5: 0.725571552,
    30: 0.7317,
    30.5: 0.734741009,
    31: 0.73776948,
    31.5: 0.740785574,
    32: 0.74378943,
    32.5: 0.746781211,
    33: 0.74976104,
    33.5: 0.752729087,
    34: 0.75568551,
    34.5: 0.758630378,
    35: 0.76156384,
    35.5: 0.764486065,
    36: 0.76739717,
    36.5: 0.770297266,
    37: 0.7731865,
    37.5: 0.776064962,
    38: 0.77893275,
    38.5: 0.781790055,
    39: 0.78463697,
    39.5: 0.787473578,
    40: 0.79030001,
}

leagues = {
    "great": 1500,
    "ultra": 2500,
    "master": 20000
}

floors = {
    "wild": 0,
    "wb": 4,
    "best": 5,
    "raid": 10,
    "lucky": 12,
}


def compute_cp(ind_atk, ind_def, ind_sta, base_atk, base_def, base_sta):
    out = {}
    for lvl in range(1, 41 * 2):
        lvl = float(lvl) / 2
        if lvl in cp_multiplier:
            m = cp_multiplier[lvl]
            attack = (base_atk + ind_atk) * m
            defense = (base_def + ind_def) * m
            stamina = (base_sta + ind_sta) * m
            cp = int(max(math.floor(attack * defense**0.5 * stamina**0.5) / 10, 10))
            out[cp] = [lvl, round(attack, 2), round(defense, 2), round(
                math.floor(stamina), 2), attack * defense * math.floor(stamina)]
    return out


def iv_combo(floor):
    perm = product(range(floor, 16), repeat=3)
    for iv in perm:
        yield iv


base_dir = "compressed_iv_data"
try:
    os.mkdir(base_dir)
except:
    pass

url = "https://raw.githubusercontent.com/pokemongo-dev-contrib/pokemongo-game-master/master/versions/latest/GAME_MASTER.json"
response = urlopen(url)
data = json.loads(response.read())

for itemTemplates in data["itemTemplates"]:
    if "pokemonSettings" in itemTemplates:
        pSettings = itemTemplates["pokemonSettings"]
        pTemplate = itemTemplates["templateId"]
        pId = pSettings["pokemonId"]
        pNumber = pTemplate.split("_")[0].lstrip("V0")
        if "SHADOW" in pTemplate:
            continue
        if "NORMAL" in pTemplate:
            continue
        if "PURIFIED" in pTemplate:
            continue
        print(pNumber, pTemplate)
        pForm = pSettings["form"] if "form" in pSettings else pId
        pFormClean = pForm.replace("_", "") if pForm else None

        baseAttack = pSettings["stats"]["baseAttack"]
        baseDefense = pSettings["stats"]["baseDefense"]
        baseStamina = pSettings["stats"]["baseStamina"]

        for league in leagues:
            try:
                os.mkdir(base_dir + "/" + league)
            except:
                pass

            for floor in floors:
                try:
                    os.mkdir(base_dir + "/" + league + "/" + floor)
                except:
                    pass
                allranks = {}

                for combo in iv_combo(floors[floor]):
                    patk, pdef, psta = combo
                    cps = compute_cp(patk, pdef, psta, baseAttack, baseDefense, baseStamina)

                    for x in sorted(cps):
                        if x <= leagues[league]:
                            iv_precent = ((patk + pdef + psta) / 45) * 100
                            cp = [patk, pdef, psta, iv_precent, x] + cps[x]
                            continue
                        else:
                            break
                    allranks[(pdef, patk, psta)] = cp

                rank = 1
                max_sp = 0
                content = "%s,%s,,,,,,,,,,\r\n" % (pNumber, pForm)
                content += "Rank,ATK,DEF,HP,IV %,CP,LVL,ATK,DEF,HP,SP,%\r\n"

                for key, value in sorted(allranks.items(), key=lambda item: (item[1][9], item[1][2]), reverse=True):
                    if rank == 1:
                        max_sp = value[9]
                    value.append(round((value[9] / max_sp) * 100, 2))
                    value = [rank] + value
                    content += str(value).replace(" ", "").lstrip("[").rstrip("]") + "\r\n"
                    rank += 1

                with gzip.open(base_dir + "/" + league + "/" + floor + "/" + pFormClean.lower() + '.csv.gz', 'wb') as f:
                    f.write(content.encode())
                f.close()
