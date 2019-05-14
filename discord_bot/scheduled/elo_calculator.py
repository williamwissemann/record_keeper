from Storage import UserStats

import asyncio
import random
import datetime
import math
import sys
import json
import os

os.chdir(os.path.abspath(__file__).replace("elo_calculator.py", ""))


def Probability(rating1, rating2):
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))


def EloRating(Ra, Rb, K, d):
    Pb = Probability(Ra, Rb)
    Pa = Probability(Rb, Ra)
    if (d == 1):
        Ra = Ra + K * (1 - Pa)
        Rb = Rb + K * (0 - Pb)
    elif (d == 0.5):
        Ra = Ra + K * (0.5 - Pa)
        Rb = Rb + K * (0.5 - Pb)
    else:
        Ra = Ra + K * (0 - Pa)
        Rb = Rb + K * (1 - Pb)
    return (Ra, Rb)

if __name__ == "__main__":
    with open("/usr/src/RecordKeeperBot/discord_bot/RecordKeeperBot.json") as f:
        settings = json.load(f)
        environment = settings[settings["settings"]["environment"]]

    usdb = UserStats("/usr/src/RecordKeeperBot/database/" + environment["database"])
    for table in usdb.pvp_leagues:
        dict_elo = {}
        for (uuid, update_at, gamertag, gamertag_winner, elo_winner, elo_winner_change,
                gamertag_loser, elo_loser, elo_loser_change, note) in usdb.get_recent_pvp_no_limit(table):

            if gamertag_winner not in dict_elo:
                dict_elo[gamertag_winner] = 1200.0
            if gamertag_loser not in dict_elo:
                dict_elo[gamertag_loser] = 1200.0

            Ra = dict_elo[gamertag_winner]
            Rb = dict_elo[gamertag_loser]
            Ra, Rb = EloRating(Ra, Rb, 30, 1)
            elo_winner = Ra
            elo_winner_change = Ra - dict_elo[gamertag_winner]
            elo_loser = Rb
            elo_loser_change = Rb - dict_elo[gamertag_loser]
            dict_elo[gamertag_winner] = elo_winner
            dict_elo[gamertag_loser] = elo_loser

            usdb.update_elo(table, uuid, elo_winner, elo_winner_change, elo_loser, elo_loser_change)

        for p in dict_elo:
            usdb.update_elo_player(table + "_elo", p, dict_elo[p])
