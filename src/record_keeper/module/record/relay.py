from typing import Union

from record_keeper import STORAGE
from record_keeper.module.admin.query import (
    get_listeners,
    has_listener,
    remove_listener,
    update_listener,
)
from record_keeper.utilities.helpers import list_to_list, find_table_name
from record_keeper.utilities.message import MessageWrapper


class RecordRelay:
    def __init__(self):
        pass

    async def relay(
        self,
        msg: MessageWrapper,
    ) -> Union[str, None]:

        if not has_listener(msg.guild_id, msg.channel_id, "record-keeper"):
            # incorrect scope or permission do not continue
            return

        response = None
        delete_after = 120

        # supported commands
        if msg.cmd == "up":
            response = self.up(msg)
        elif msg.cmd == "ls":
            response = self.ls(msg)
        elif msg.cmd == "lb":
            response = self.lb(msg)
        elif msg.cmd == "!uuid":
            response = self.uuid(msg)
        elif msg.cmd == "!del":
            response = self.delete(msg)

        # send the response to discord
        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

    def up(self, message):
            

        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        if "user" in message:
            identifier = get_discord_id(message, message["user"])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        try:
            medal = find_table_name(message["args"][0])
            value = message["args"][1]
            value = value.replace(",", "")
            note = message["note"] if "note" in message else ""
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if medal not in self.usdb.accepted_tables:
            return "Bidoof, " + message["args"][0] + " can not be found"

        try:
            self.usdb.update_medal(
                server, medal, str(identifier), value, message["date"], note
            )
        except Exception:
            return "Bidoof, " + value + " can not be found"

        if str(identifier) != str(message["raw_msg"].author.id):
            bm = (
                "<@!"
                + str(identifier)
                + "> stats were updated by "
                + "<@!"
                + str(message["raw_msg"].author.id)
                + ">"
            )
            return bm
        else:
            bm = bot_message.create_recent5(server, self.usdb, medal, str(identifier))
            bm += bot_message.create_stats(server, self.usdb, medal, str(identifier))
            return bm

    def ls(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        try:
            medal = self.find_table_name(message["args"][0])
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"
        if len(message["args"]) > 1:
            search_term = message["args"][1]
            identifier = get_discord_id(message, search_term)
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        if not (medal in self.usdb.accepted_tables or medal in self.usdb.pvp_leagues):
            return "There was an issue listing the stat for " + message["args"][0]

        if medal in self.usdb.pvp_leagues:
            bm = bot_message.create_recent_pvp10(
                server, self.usdb, message, medal, identifier
            )
            if "Bidoof" not in bm:
                bm += bot_message.create_stats(
                    server, self.usdb, medal, str(identifier)
                )
        else:
            bm = bot_message.create_recent5(server, self.usdb, medal, identifier)
            if "Bidoof" not in bm:
                bm += bot_message.create_stats(
                    server, self.usdb, medal, str(identifier)
                )
        return bm

    def uuid(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        try:
            medal = self.find_table_name(message["args"][0])
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"
        if len(message["args"]) > 1:
            search_term = message["args"][1]
            identifier = get_discord_id(message, search_term)
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        if not (medal in self.usdb.accepted_tables or medal in self.usdb.pvp_leagues):
            return "There was an issue listing the stat for " + message["args"][0]

        if medal in self.usdb.pvp_leagues:
            bm = bot_message.create_uuid_table_pvp(
                server, self.usdb, message, medal, identifier
            )
        else:
            bm = bot_message.create_uuid_table(server, self.usdb, medal, identifier)
        return bm

    def lb(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        try:
            medal = self.find_table_name(message["args"][0])
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not (medal in self.usdb.accepted_tables or medal in self.usdb.pvp_leagues):
            return "There was an issue listing the stat for " + message["args"][0]

        if medal in self.usdb.pvp_leagues:
            bm = bot_message.create_elo10(server, self.usdb, medal, message)
        else:
            bm = bot_message.create_leaderboard10(server, self.usdb, medal, message)
        return bm

    def delete(self, message):
        try:
            server = message["raw_msg"].guild.id
        except Exception:
            server = "ViaDirectMessage"

        if "user" in message:
            identifier = get_discord_id(message, message["user"])
        else:
            identifier = message["raw_msg"].author.id
        if not identifier:
            return "Bidoof, cannot find user"

        try:
            medal = self.find_table_name(message["args"][0])
            value = message["args"][1]
            value = value.replace(",", "")
        except Exception:
            return "Bidoof, sorry, something went wrong, try !help for more info"

        if not medal:
            return "Bidoof, " + message["args"][0] + " can not be found"

        self.usdb.delete_row(server, medal, identifier, value)
        if medal in self.usdb.pvp_leagues:
            bm = bot_message.create_recent_pvp10(
                server, self.usdb, message, medal, identifier
            )
        else:
            bm = bot_message.create_recent5(server, self.usdb, medal, identifier)
        return bm



"""
    def get_day_avg(self, server, table, user, days=7):
        " calculates average based on number of days ""
        sql_string = "SELECT * FROM " + str(table)
        sql_string += " WHERE gamertag = '" + str(user) + "'"
        if not server == "ViaDirectMessage":
            sql_string += (
                " AND ( server_id = '"
                + str(server)
                + "' OR server_id = 'ViaDirectMessage')"
            )
        sql_string += " AND update_at >= datetime('now', '-" + str(days) + " days') "
        sql_string += " AND update_at <=  datetime('now','+1 day') "
        sql_string += " ORDER BY update_at ASC"

        recent = []
        average_increase = []
        for row in self.c.execute(sql_string):
            recent.append(row)
            if len(recent) > 1:
                average_increase.append(
                    recent[len(recent) - 1][4] - recent[len(recent) - 2][4]
                )
            else:
                continue

        if len(recent) > 0:
            y, m, d = recent[0][2].split("T")[0].split(" ")[0].split("-")
            min_date = datetime.datetime(int(y), int(m), int(d))
            y, m, d = (
                recent[(len(recent) - 1)][2].split("T")[0].split(" ")[0].split("-")
            )
            max_date = datetime.datetime(int(y), int(m), int(d))
            day_diff = (max_date - min_date).days + 1
            return float(sum(average_increase)) / day_diff
        return 0.0

    @BOT.database.get
    def get_leaders(self, server, table):
        if str(table) == "Stardust":
            sql = "SELECT uuid, server_id, update_at, gamertag, value, note FROM " + str(
                table
            )
            if not server == "ViaDirectMessage":
                sql += (
                    " WHERE ( server_id = '"
                    + str(server)
                    + "' OR server_id = 'ViaDirectMessage')"
                )
            sql += " GROUP BY gamertag"
            sql += " ORDER BY value DESC, update_at ASC"
            sql += " LIMIT 25"
        else:
            sql = (
                "SELECT uuid, server_id, update_at, gamertag, MAX(value), note FROM "
                + str(table)
            )
            if not server == "ViaDirectMessage":
                sql += (
                    " WHERE ( server_id = '"
                    + str(server)
                    + "' OR server_id = 'ViaDirectMessage')"
                )
            sql += " GROUP BY gamertag"
            sql += " ORDER BY value DESC, update_at ASC"
            sql += " LIMIT 25"
        return sql
"""
