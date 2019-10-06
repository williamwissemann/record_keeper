import discord.ext.test as dpytest
import discord_bot.RecordKeeperBot as rk


def test_bot():
    bot = rk.on_message()

    # Load any extensions/cogs you want to in here

    dpytest.configure(bot)

    dpytest.message("!help")
    dpytest.verify_message("[Expected help output]")
