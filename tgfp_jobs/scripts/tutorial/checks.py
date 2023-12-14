""" Sample discord bot """
from config import get_config
# pylint: disable=F0401
import discord
from discord.ext import commands

config = get_config()


class NotOwner(commands.CheckFailure):
    ...


def is_owner():
    async def predicate(ctx):
        if ctx.author.id != ctx.guild.owner_id:
            raise NotOwner("Hey You are not the owner!")
        return True
    return commands.check(predicate)


def run():
    """ Run the bot """
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"User: {bot.user} (ID: {bot.user.id})")

    @bot.command()
    @is_owner()
    async def say(ctx, what = "What?"):
        await ctx.send(what)

    @say.error
    async def say_error(ctx, error):
        if isinstance(error, NotOwner):
            await ctx.send("Permission Denied")

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
