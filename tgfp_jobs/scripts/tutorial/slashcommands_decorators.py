""" Sample discord bot """
import enum
# pylint: disable=F0401
from typing import Literal
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

    @bot.tree.command()
    @app_commands.describe(text_to_send="Simon Says this..")
    @app_commands.rename(text_to_send="message")
    async def say(interaction: discord.Interaction, text_to_send: str):
        await interaction.response.send_message(f"{text_to_send}", ephemeral=True)

    @bot.tree.command()
    async def drink(interaction: discord.Interaction, choice: Literal['beer', 'milk', 'tea']):
        await interaction.response.send_message(f"{choice}", ephemeral=True)

    @bot.tree.command()
    async def eat(interaction: discord.Interaction, choice: Food):
        await interaction.response.send_message(f"{choice}", ephemeral=True)

    @bot.tree.command()
    @app_commands.choices(choice=[
        app_commands.Choice(name="red", value="1"),
        app_commands.Choice(name="green", value="2"),
        app_commands.Choice(name="blue", value="3")
    ])
    async def color(interaction: discord.Interaction, choice: app_commands.Choice[str]):
        await interaction.response.send_message(f"{choice}", ephemeral=True)

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
