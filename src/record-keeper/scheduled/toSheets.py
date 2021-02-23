from __future__ import print_function

# import requests
import csv
import json
import os
import sys
import time
from datetime import date, datetime, timedelta

import discord
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools
from RecordKeeperUtils import get_discord_name
from Storage import UserStats

os.chdir(os.path.abspath(__file__).replace("toSheets.py", ""))

server = "487986792868478987"
dclient = discord.Client()


with open("/usr/src/RecordKeeperBot/discord_bot/RecordKeeperBot.json") as f:
    settings = json.load(f)
    bot_environment = settings["bot_settings"]["environment"]
    # this logic needs fixing (via admin activate/deactiviate)
    settings["bot_settings"][settings["bot_settings"]["environment"]]

db_path = "{}{}".format(
    "/usr/src/RecordKeeperBot/database/",
    settings["bot_settings"][bot_environment]["database"])
print(db_path)
usdb = UserStats(db_path, "IGNORE_VERSION")

if server not in settings["server_settings"]:
    print("google sheets is off")
    sys.exit()

members = {}


@client.event
async def on_ready():
    print("> signed in as: " + dclient.user.name)
    print("> with client id: " + str(dclient.user.id))
    print('> Discord.py Version: {}'.format(discord.__version__))

    for member in dclient.get_all_members():
        members[str(member.id)] = str(member)

    await dclient.close()
dclient.run(settings["bot_settings"][bot_environment]["discord_token"])

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SPREADSHEET_ID = settings["server_settings"][server]["google_sheet"]["spreadsheet_id"]

# login to google drive, and grant permissions for this script
store = file.Storage(settings["server_settings"][server]["google_sheet"]["path_to_token"])
creds = store.get()

if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('./google-sheets-creds/token.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))

y_offset = 1
x_list = ["A", "I", "Q"]
x_offset = 0


def label(text):
    global y_offset
    global x_offset
    # The ID of the spreadsheet to update.
    spreadsheet_id = SPREADSHEET_ID

    # The A1 notation of the values to update.
    print(text, str(x_list[x_offset]) + str(y_offset - 1))
    range_ = 'Leaderboard!' + str(x_list[x_offset]) + str(y_offset)
    # How the input data should be interpreted.
    value_input_option = 'RAW'

    value_range_body = {
        "values": [[text]]
    }

    request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option, body=value_range_body)
    request.execute()
    y_offset += 1


def update_speadsheet(value_body):
    global y_offset
    global x_offset
    # The ID of the spreadsheet to update.
    spreadsheet_id = SPREADSHEET_ID

    # The A1 notation of the values to update.
    range_ = 'Leaderboard!' + str(x_list[x_offset]) + str(y_offset)
    # How the input data should be interpreted.
    value_input_option = 'RAW'

    print(value_body)

    value_range_body = {
        "values": value_body
    }

    request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option, body=value_range_body)
    request.execute()

    x_offset = (x_offset + 1) % 3
    print(x_offset, y_offset)
    if x_offset == 0:
        y_offset += 13


def build_tables(array):
    global y_offset
    global x_offset
    for el in array:
        try:
            board = usdb.get_leaders(server, el)
            max_val = board[0][4]
            cnt = 1
            table = [[el, "", "", "", "Average per day"],
                     ["Rank", "Gamertag", "Value", "", "Past Week", "Past Month", "Past 90 Days"]]
            for player in board[0:10]:
                array = []
                val = player[4]
                # print(player)
                try:
                    diff = val / max_val
                except:
                    diff = 0
                gt = player[3]

                array.append(cnt)
                # print(gt, members[gt])

                array.append((str(members[gt]).split('#')[0]))
                array.append(val)
                array.append(diff)
                array.append(usdb.get_day_avg(server, el, gt, 7))
                array.append(usdb.get_day_avg(server, el, gt, 30))
                array.append(usdb.get_day_avg(server, el, gt, 90))
                cnt += 1
                table.append(array)
        except:
            continue
        update_speadsheet(table)
        time.sleep(3)


def build_tables_raids(array):
    global y_offset
    global x_offset
    for el in array:
        board = usdb.get_leaders(server, el)
        print(board)
        try:
            max_val = board[0][4]
        except:
            max_val = 1
        cnt = 1
        table = [[el, "", "", "", ""],
                 ["Rank", "Gamertag", "Time", "", "Notes"]]
        for player in board[0:10]:
            array = []
            val = player[3]
            try:
                diff = val / max_val
            except:
                diff = 0
            gt = player[3]
            note = player[5]

            array.append(cnt)
            array.append(str(gt).split('#')[0])
            array.append(val)
            array.append(diff)
            array.append(note)
            cnt += 1
            table.append(array)
        for row in table:
            print(row)
        update_speadsheet(table)
        time.sleep(3)


x_offset = 0
label("Basics")
build_tables(usdb.basic_tables)

y_offset += 12 + 2
x_offset = 0
label("Badges")
build_tables(usdb.badge_tables)

y_offset += 12 + 2
x_offset = 0
label("Types")
build_tables(usdb.type_tables)

y_offset += 1
x_offset = 0
label("Custom")
build_tables(usdb.custom_tables)

y_offset += 12 + 2
x_offset = 0
#  label("Raids")
#  build_tables_raids(usdb.raid_tables)
