""" Sample discord bot """
import enum
import typing
# pylint: disable=F0401
from typing import Literal, List
from discord import app_commands
from config import get_config
import discord
from discord.ext import commands

config = get_config()

class SlapReason(typing.NamedTuple):
    reason: str


class SlapTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> SlapReason:
        return SlapReason(reason=f"*** {value} ***")

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
    async def slap(
            interaction: discord.Interaction,
            reason: app_commands.Transform[SlapReason, SlapTransformer]
    ):
        await interaction.response.send_message(f"Ouch {reason}", ephemeral=True)

    @bot.tree.command()
    async def range(
            interaction: discord.Interaction,
            value: app_commands.Range[int, None, 10]
    ):
        await interaction.response.send_message(f"Ouch {value}", ephemeral=True)

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
