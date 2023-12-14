""" Sample discord bot """
import enum
# pylint: disable=F0401
from typing import Literal, List
from discord import app_commands
from config import get_config
import discord
from discord.ext import commands

config = get_config()


class Food(enum.Enum):
    apple = 1
    banana = 2
    cherry = 3


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

    async def drink_autocompletion(
            interaction: discord.Interaction,
            current: str
    ) -> List[app_commands.Choice[str]]:
        data = []
        for drink_choice in ['beer', 'milk', 'tea', 'coffee', 'juice']:
            if current.lower() in drink_choice.lower():
                data.append(app_commands.Choice(name=drink_choice, value=drink_choice))
        return data

    @bot.tree.command()
    @app_commands.autocomplete(item=drink_autocompletion)
    async def drink(interaction: discord.Interaction,
                    item: str
                    ):
        await interaction.response.send_message(f"{item}", ephemeral=True)


    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
