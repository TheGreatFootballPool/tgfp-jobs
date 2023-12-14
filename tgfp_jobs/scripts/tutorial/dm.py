""" Sample discord bot """
from config import get_config
# pylint: disable=F0401
import discord
from discord.ext import commands

config = get_config()


def run():
    """ Run the bot """
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"User: {bot.user} (ID: {bot.user.id})")

    @bot.command()
    async def ping(ctx):
        # await ctx.message.author.send("hello")
        user = discord.utils.get(bot.get_guild(config.DISCORD_GUILD_ID).members, nick="TestUser")
        if user:
            await user.send("Hello 2")

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
