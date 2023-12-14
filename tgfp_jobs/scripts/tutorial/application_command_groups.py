""" Sample discord bot """
# pylint: disable=F0401
from config import get_config
import discord
from discord.ext import commands

config = get_config()


def run():
    """ Run the bot """
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    guild_id: discord.Object = discord.Object(id=config.DISCORD_GUILD_ID)

    @bot.event
    async def on_ready():
        print(f"User: {bot.user} (ID: {bot.user.id})")
        await bot.load_extension("slash_commands.welcome")
        bot.tree.copy_global_to(guild=guild_id)
        await bot.tree.sync(guild=guild_id)

    @bot.command()
    async def sync(ctx) -> None:
        bot.tree.copy_global_to(guild=guild_id)
        synced = await bot.tree.sync(guild=guild_id)
        await ctx.send(
            f"Synced {len(synced)} GUILD commands to the current guild."
        )

    # noinspection PyUnresolvedReferences
    @bot.tree.command(description="Welcomes user", nsfw=True)
    async def ciao(interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Ciao! {interaction.user.mention}"
        )

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
