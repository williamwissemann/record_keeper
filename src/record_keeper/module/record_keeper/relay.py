from typing import Union

from record_keeper import BOT
from record_keeper.module.admin.query import has_listener
from record_keeper.module.record_keeper.query import (
    delete_medal,
    get_avg_per_day,
    get_leaderboard,
    get_recent,
    get_uuid_recent,
    update_medal,
)
from record_keeper.utilities.helpers import (
    clean_date_string,
    force_str_length,
    get_medal,
)
from record_keeper.utilities.message import MessageWrapper


class RecordRelay:
    async def relay(
        self,
        msg: MessageWrapper,
    ) -> Union[str, None]:

        response = None
        delete_after = 120

        active = has_listener(msg.guild_id, msg.channel_id, "record-keeper")
        if active or msg.direct_message:
            if msg.cmd == "up":
                response = self.up(msg)
            elif msg.cmd == "ls":
                response = self.ls(msg)
            elif msg.cmd == "lb":
                response = self.lb(msg)

        active = has_listener(msg.guild_id, msg.channel_id, "deletable-data")
        if active or msg.direct_message:
            if msg.cmd == "uuid":
                response = self.uuid(msg)
            elif msg.cmd == "del":
                response = self.delete(msg)

        if response:
            return await msg.send_message(
                response,
                delete_after,
                new_message=True,
            )

        return None

    def up(self, msg):
        user = msg.user.id
        if msg.find_by_slug:
            user = msg.get_discord_id(msg.find_by_slug)
            if not user:
                return "Bidoof, cannot find user"

        try:
            medal = get_medal(msg)
            if not medal:
                return f"Bidoof, {msg.arguments[0]} can not be found"

            value = msg.arguments[1]
            value = value.replace(",", "")
        except Exception:
            return BOT.HELP_PROMPT

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
            return f"<@!{user}> stats were updated by <@!{msg.user.id}>"
        else:
            bm = self.create_recent(msg, medal, msg.user.id)
            bm += self.create_stats(msg, medal, msg.user.id)
            return bm

    def ls(self, msg):
        user = msg.user.id
        if len(msg.arguments) > 1:
            user = msg.get_discord_id(msg.arguments[1])
            if not user:
                return "Bidoof, cannot find user"

        try:
            medal = get_medal(msg)
            if not medal:
                return f"Bidoof, {msg.arguments[0]} can not be found"
        except Exception:
            return BOT.HELP_PROMPT

        bm = self.create_recent(msg, medal, user)
        bm += self.create_stats(msg, medal, user)
        return bm

    def create_recent(self, msg, medal, user):
        """Creates a most recent 5 for a medal, gamertag"""

        recent_list = get_recent(msg.guild_id, medal, user, limit=5)
        if len(recent_list) > 0:
            msg = f"<@!{user}>'s last 5 entries for {medal}\n```"
            msg += "Date       |Value      |Note \n"
            msg += "-----------+-----------+-----------\n"
            for el in recent_list:
                date, value, note = el

                date = clean_date_string(date)

                value = str(value).split(".")[0]
                value = force_str_length(value, length=9)

                note = force_str_length(note, length=10)

                msg += f"{date} | {value} | {note} \n"
            msg += "```"
            return msg
        else:
            return "Bidoof, nothing to see here"

    def create_stats(self, server, medal, user):
        msg = (
            "averages per day\n"
            "```"
            "Past Week  |Past Month |Past 90 Days\n"
            "-----------+-----------+------------\n"
        )

        day7 = get_avg_per_day(server, medal, user, 7)[0][0]
        day7 = day7 if day7 else 0
        day7 = force_str_length(round(day7, 2), 10)

        day30 = get_avg_per_day(server, medal, user, 30)[0][0]
        day30 = day30 if day30 else 0
        day30 = force_str_length(round(day30, 2), 9)

        day90 = get_avg_per_day(server, medal, user, 90)[0][0]
        day90 = day90 if day90 else 0
        day90 = force_str_length(round(day90, 2), 9)

        msg += f"{day7} | {str(day30)} | {str(day90) }\n```"
        return msg

    def lb(self, msg):
        try:
            medal = get_medal(msg)
            if not medal:
                return f"Bidoof, {msg.arguments[0]} can not be found"
        except Exception:
            return BOT.HELP_PROMPT

        bm = self.create_leaderboard(msg, medal)

        return bm

    def create_leaderboard(server, msg, medal):
        leaderboard = get_leaderboard(msg.guild_id, medal, limit=10)
        if len(leaderboard) > 0:
            bm = (
                f"Leaderboard for {medal} \n"
                "```"
                "   |Value      |Name\n"
                "---+-----------+--------------\n"
            )
            cnt = 0
            for el in leaderboard:

                date, user, value, note = el

                date = clean_date_string(date)

                value = str(value).split(".")[0]
                value = force_str_length(value, length=9)

                discord_name = msg.get_discord_name(user)
                discord_name = force_str_length(discord_name, length=16)

                cnt += 1
                idx = force_str_length(cnt, length=2)

                bm += f"{idx} | {value} | {discord_name} \n"
                if note != "":
                    bm += f"---+-----------+> {note} \n"
            bm += "```"
            return bm
        else:
            return "Bidoof, nothing to see here"

    def uuid(self, msg):
        user = msg.user.id
        if msg.find_by_slug:
            user = msg.get_discord_id(msg.find_by_slug)
            if not user:
                return "Bidoof, cannot find user"

        try:
            medal = get_medal(msg)
            if not medal:
                return f"Bidoof, {msg.arguments[0]} can not be found"
        except Exception:
            return BOT.HELP_PROMPT

        bm = self.create_uuid_table(msg, medal, user)

        return bm

    def create_uuid_table(self, msg, medal, user):
        """
        Creates a most recent 5 for a medal, gamertag with uuid
        """
        uuid_list = get_uuid_recent(msg.guild_id, medal, user, limit=5)
        if len(uuid_list) > 0:
            msg = f"<@!{user}>'s last 5 entries for {medal}\n```"
            msg += " uuid                                | value     \n"
            msg += "-------------------------------------+-----------\n"
            for el in uuid_list:
                uuid, value = el

                value = str(value).split(".")[0]
                value = force_str_length(value, length=9)

                msg += f"{uuid} | {value} \n"
            msg += "```"
            return msg
        else:
            return "Bidoof, nothing to see here"

    def delete(self, msg):
        user = msg.user.id
        if msg.find_by_slug:
            user = msg.get_discord_id(msg.find_by_slug)
            if not user:
                return "Bidoof, cannot find user"

        try:
            medal = get_medal(msg)
            if not medal:
                return f"Bidoof, {msg.arguments[0]} can not be found"
            uuid = msg.arguments[1]
        except Exception:
            return BOT.HELP_PROMPT

        try:
            delete_medal(
                msg.guild_id,
                medal,
                user,
                uuid,
            )
        except Exception:
            return f"Bidoof, {uuid} is invalid for {medal}"

        if str(user) != str(msg.user.id):
            return f"<@!{user}> stats were updated by <@!{msg.user.id}>"
        else:
            bm = self.create_recent(msg, medal, msg.user.id)
            bm += self.create_stats(msg, medal, msg.user.id)
            return bm
