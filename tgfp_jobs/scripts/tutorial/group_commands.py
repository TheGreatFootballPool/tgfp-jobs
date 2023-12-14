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
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"User: {bot.user} (ID: {bot.user.id})")

    @bot.group()
    async def math(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(f"No, {ctx.subcommand_passed} does not belong to math")

    @math.group()
    async def simple(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(f"No, {ctx.subcommand_passed} does not belong to math")

    @simple.command()
    async def add(ctx, one: int, two: int):
        await ctx.send(one + two)

    @simple.command()
    async def subtract(ctx, one: int, two: int):
        await ctx.send(one - two)

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
