""" Sample discord bot """
# pylint: disable=F0401
from config import get_config
import discord
from discord.ext import commands

config = get_config()


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
    async def ping(ctx):
        embed = discord.Embed(
            colour=discord.Colour.dark_teal(),
            description="this is the description",
            title="this is the title"
        )
        embed.set_footer(text="this is the footer")
        embed.set_author(name="John", url="https://johnsturgeon.me")
        embed.set_thumbnail(
            url="https://www.dropbox.com/scl/fi/ios1k0csdxnodn1a5w9pw/"
                "john.southpark.png?rlkey=7nrpgp2xs4sxi2xpknhxyq3ev&raw=1"
        )
        embed.set_image(url="https://www.dropbox.com/scl/fi/vqdoll2c7138gb9ojcaxc/tgfp_logo.png?rlkey=a7ro4z9le78kikyv3x3n1um8v&raw=1")
        embed.add_field(name="Channel", value="https://johnsturgeon.me")
        embed.add_field(name="Website", value="https://google.com")
        embed.insert_field_at(1, name="Tree", value="linktree.com")
        await ctx.send(embed=embed)

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
