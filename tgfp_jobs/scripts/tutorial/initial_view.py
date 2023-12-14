""" Sample discord bot """
from typing import Optional

# pylint: disable=F0401
from config import get_config
import discord
from discord.ext import commands

config = get_config()


class SimpleView(discord.ui.View):

    foo_bar: Optional[bool] = None
    message: Optional[discord.Message] = None

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self) -> None:
        await self.message.channel.send("Timeout")
        await self.disable_all_items()

    @discord.ui.button(
        label="Hello",
        style=discord.ButtonStyle.success
    )
    async def hello(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("World")   # noqa
        self.foo_bar = True
        self.stop()

    @discord.ui.button(
        label="49ers",
        style=discord.ButtonStyle.gray,
        emoji="<:49ers:533776540807331873>"
    )
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling")   # noqa
        self.foo_bar = True
        self.stop()


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

    @bot.command()
    async def button(ctx):
        view = SimpleView(timeout=20)
        # a_button = discord.ui.Button(label="Click me")
        # view.add_item(a_button)
        message = await ctx.send(view=view)
        view.message = message
        await view.wait()
        await view.disable_all_items()

        if view.foo_bar is None:
            print("Timeout")
        elif view.foo_bar is True:
            print("Ok")
        else:
            print("Cancelled")

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
