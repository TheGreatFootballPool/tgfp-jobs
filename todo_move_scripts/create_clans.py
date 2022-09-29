""" Script to create / sync clans and clan membership between discord and the Mongo DB """
import os

from discord import Guild
from tgfp_lib import TGFP, TGFPClan

import discord

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == "The Great Football Pool":
            for role in guild.roles:
                print(role.name)
                print(role.id)
                print("=======")
            sync_db_roles_with_discord_guild(guild)


@client.event
async def on_message(message):
    if message.author == client.user:
        print("ourselves")
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


def sync_db_roles_with_discord_guild(guild: Guild):
    tgfp = TGFP()
    for role in guild.roles:
        clan: TGFPClan = tgfp.find_clan(discord_role_id=role.id)
        if clan:
            print(f"Clearing all members from clan")
            clan.delete_all_members()
            for role_member in role.members:
                print(f"\tAdding: {role_member.display_name} to clan")
                clan.add_member(role_member.id)


def main():
    client.run(os.getenv('DISCORD_AUTH_TOKEN'))


if __name__ == '__main__':
    main()
