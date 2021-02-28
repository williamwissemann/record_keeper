from typing import Union

from record_keeper import STORAGE
from record_keeper.module.admin.query import has_listener
from record_keeper.module.record.query import get_avg_per_day, get_recent, update_medal
from record_keeper.utilities.helpers import (
    clean_date_string,
    find_table_name,
    force_str_length,
)
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

    def up(self, msg):
        user = msg.user.id
        if msg.find_by_slug:
            user = msg.get_discord_id(msg.find_by_slug)
            if not user:
                return "Bidoof, cannot find user"

        try:
            medal = find_table_name(msg.arguments[0])
            value = msg.arguments[1]
            value = value.replace(",", "")
        except Exception:
            return "Bidoof, sorry, something went wrong," "try !help for more info"

        if medal not in STORAGE.accepted_tables:
            return f"Bidoof, {medal} can not be found"

        try:
            update_medal(
                msg.guild_id,
                medal,
                user,
                value,
                msg.date,
                msg.note,
            )
        except Exception:
            return f"Bidoof, {value} is invalid for {medal}"

        if str(user) != str(msg.user.id):
            return f"<@!{user}>" "stats were updated by" f"<@!{msg.user.id}>"
        else:
            bm = self.create_recent5(msg, medal, msg.user.id)
            bm += self.create_stats(msg, medal, msg.user.id)
            return bm

    def ls(self, msg):
        user = msg.user.id
        if msg.find_by_slug:
            user = msg.get_discord_id(msg.find_by_slug)
            if not user:
                return "Bidoof, cannot find user"

        try:
            medal = find_table_name(msg.arguments[0])
        except Exception:
            return "Bidoof, sorry, something went wrong," "try !help for more info"

        if medal not in STORAGE.accepted_tables:
            return f"Bidoof, {medal} can not be found"

        if str(user) != str(msg.user.id):
            return f"<@!{user}>" "stats were updated by" f"<@!{msg.user.id}>"
        else:
            bm = self.create_recent5(msg, medal, msg.user.id)
            bm += self.create_stats(msg, medal, msg.user.id)
            return bm

    def create_recent5(self, msg, medal, user):
        """Creates a most recent 5 for a medal, gamertag"""

        recent_list = get_recent(msg.guild_id, medal, user, limit=5)
        if len(recent_list) > 0:
            msg = f"<@!{user}>'s last 5 entries for {medal}\n```"
            msg += "Date       |Value      |Note \n"
            msg += "-----------+-----------+-----------\n"
            for el in recent_list:
                _, _, date, _, value, note = el

                date = clean_date_string(date)

                value = str(value).split(".")[0]
                value = force_str_length(value, length=10)

                note = force_str_length(note, length=10)

                msg += f"{date} | {value} | {note} \n"
            msg += "```"
            return msg
        else:
            return "Bidoof, nothing to see here"

    def create_stats(server, usdb, medal, user):
        msg = (
            "averages per day\n"
            "```"
            "Past Week  |Past Month |Past 90 Days\n"
            "-----------+-----------+------------\n"
        )

        day7 = get_avg_per_day(server, medal, user, 7)[0][0]
        day7 = force_str_length(round(day7, 2), 10)

        day30 = get_avg_per_day(server, medal, user, 30)[0][0]
        day30 = force_str_length(round(day30, 2), 10)

        day90 = get_avg_per_day(server, medal, user, 90)[0][0]
        day90 = force_str_length(round(day90, 2), 10)

        msg += f"{day7} | {str(day30)} | {str(day90) }\n```"
        return msg

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
