""" Sample discord bot """
from config import get_config
# pylint: disable=F0401
import discord
from discord.ext import commands
from cogs.greetings import Greetings

config = get_config()

CMDS_DIR = config.BASE_DIR / "cmds"


def run():
    """ Run the bot """
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"User: {bot.user} (ID: {bot.user.id})")

        await bot.load_extension("cogs.greetings")

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
