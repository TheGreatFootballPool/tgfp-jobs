""" Sample discord bot """
from config import get_config
# pylint: disable=F0401
import discord
from discord.ext import commands

config = get_config()


def run():
    """ Run the bot """
    discord.utils.setup_logging()
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"User: {bot.user} (ID: {bot.user.id})")

    @bot.command()
    async def sync(ctx) -> None:
        synced = await ctx.bot.tree.sync()
        print(synced)
        await ctx.send(
            f"Synced {len(synced)} global commands to the current guild."
        )

    @bot.hybrid_command()
    async def pong(ctx):
        await ctx.send("ping")

    @bot.tree.command()
    async def ciao(interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Ciao! {interaction.user.mention}",
            ephemeral=True
        )

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
