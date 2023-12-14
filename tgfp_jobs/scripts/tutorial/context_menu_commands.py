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

        bot.tree.copy_global_to(guild=guild_id)
        await bot.tree.sync(guild=guild_id)

    # noinspection PyUnresolvedReferences
    @bot.tree.context_menu(name="Show join date")
    async def get_joined_date(interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(
            f"Member joined: {discord.utils.format_dt(member.joined_at)}", ephemeral=True
        )

    # noinspection PyUnresolvedReferences
    @bot.tree.context_menu(name="Report Message")
    async def report_message(interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_message(
            "Message Reported", ephemeral=True
        )

    # noinspection PyUnresolvedReferences
    @bot.tree.context_menu(name="Report Message")
    async def report_voice(interaction: discord.Interaction, channel: discord.VoiceChannel):
        await interaction.response.send_message(
            "Message Reported", ephemeral=True
        )

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
