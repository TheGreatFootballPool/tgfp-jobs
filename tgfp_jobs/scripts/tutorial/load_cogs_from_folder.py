""" Sample discord bot """
from config import get_config
# pylint: disable=F0401
import discord
from discord.ext import commands
from cogs.greetings import Greetings

config = get_config()


def run():
    """ Run the bot """
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"User: {bot.user} (ID: {bot.user.id})")

        for cog_file in config.COGS_DIR.glob("*.py"):
            if cog_file != "__init__.py":
                await bot.load_extension(f"cogs.{cog_file.name[:-3]}")

    @bot.command()
    async def reload(ctx, cog: str):
        await bot.reload_extension(f"cogs.{cog.lower()}")

    @bot.command()
    async def load(ctx, cog: str):
        await bot.load_extension(f"cogs.{cog.lower()}")

    @bot.command()
    async def unload(ctx, cog: str):
        await bot.unload_extension(f"cogs.{cog.lower()}")

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
