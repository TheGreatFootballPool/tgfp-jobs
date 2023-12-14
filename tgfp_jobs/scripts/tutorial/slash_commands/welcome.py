# pylint: disable=F0401
import discord
from discord import app_commands


class MyGroup(app_commands.Group):
    # noinspection PyUnresolvedReferences
    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("ping")

    # noinspection PyUnresolvedReferences
    @app_commands.command()
    async def pong(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong")


async def setup(bot):
    bot.tree.add_command(MyGroup(name="greetings2", description="Says Hello"))
