""" Script will check for players who have not done their picks and 'nag' @mention them """
import asyncio
import os

import hikari

ADMIN_ID = 448942240916832268

message: str = "Yo"

bot: hikari.GatewayBot = hikari.GatewayBot(
    token=os.getenv('DISCORD_AUTH_TOKEN'),
    intents=hikari.Intents.ALL
)


@bot.listen(hikari.GuildAvailableEvent)
async def guild_available(event: hikari.GuildAvailableEvent):
    global message
    member: hikari.Member
    if event.guild.name != 'The Great Football Pool':
        return

    for _, member in event.members.items():
        if member.id == ADMIN_ID:
            await member.send(message)
            break
    await asyncio.sleep(2)
    await bot.close()


def send_message(incoming_message: str):
    global message
    message = incoming_message
    bot.run()
