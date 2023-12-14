""" Sample discord bot """
# pylint: disable=F0401
from discord import Interaction
from discord._types import ClientT
from config import get_config
import discord
from discord.ext import commands
# import utils

config = get_config()


class FeedbackModal(discord.ui.Modal, title="Send us your feedback"):
    fb_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Title",
        required=False,
        placeholder="Give your feedback a title"
    )

    message = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Feedback",
        required=False,
        max_length=500,
        placeholder="Give your feedback"
    )

    user: discord.Member

    async def on_submit(self, interaction: Interaction[ClientT], /) -> None:
        channel = interaction.guild.get_channel(config.DISCORD_NAG_BOT_CHANNEL_ID)
        embed = discord.Embed(
            title="New Feedback",
            description=self.message.value,
            color=discord.Color.yellow()
        )
        embed.set_author(name=self.user.nick)
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Thank you, {self.user.nick}", ephemeral=True) # noqa

    async def on_error(self, interaction: Interaction[ClientT], error) -> None:
        ...


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
        # await utils.load_videocmds()

    @bot.tree.command()
    async def feedback(interaction: discord.Interaction):
        feedback_modal = FeedbackModal()
        feedback_modal.user = interaction.user
        await interaction.response.send_modal(feedback_modal)  # noqa

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
