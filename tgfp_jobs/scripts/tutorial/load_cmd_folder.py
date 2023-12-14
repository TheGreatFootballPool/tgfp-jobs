""" Sample discord bot """
from config import get_config
# pylint: disable=F0401
import discord
from discord.ext import commands

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

        for cmd_file in CMDS_DIR.glob("*.py"):
            print(f"Filename: {cmd_file.name}")
            if cmd_file.name != "__init__.py":
                await bot.load_extension(f"cmds.{cmd_file.name[:-3]}")

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
