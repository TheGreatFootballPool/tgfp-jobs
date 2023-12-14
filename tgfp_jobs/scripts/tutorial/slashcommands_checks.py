""" Sample discord bot """
import enum
# pylint: disable=F0401
from typing import Literal, List
from discord import app_commands
from config import get_config
import discord
from discord.ext import commands

config = get_config()


def is_owner():
    def predicate(interaction: discord.Interaction):
        if interaction.user.id == interaction.guild.owner_id:
            return True
        return False
    return app_commands.check(predicate)


def run():
    """ Run the bot """
    intents = discord.Intents.all()

    bot = commands.Bot(command_prefix="!", intents=intents)
    guild_id: discord.Object = discord.Object(id=config.DISCORD_GUILD_ID)

    @bot.event
    async def on_ready():
        print(f"User: {bot.user} (ID: {bot.user.id})")

        bot.tree.copy_global_to(guild=guild_id)
        await bot.tree.sync(guild=guild_id)

    # noinspection PyUnresolvedReferences
    @bot.tree.command()
    @is_owner()
    async def say(interaction: discord.Interaction, text_to_send: str):
        """ Simon Says ..."""
        await interaction.response.send_message(f"{text_to_send}", ephemeral=True)

    # noinspection PyUnresolvedReferences
    @say.error
    async def say_error(interaction: discord.Interaction, error):
        await interaction.response.send_message("Not allowed!", ephemeral=True)

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
