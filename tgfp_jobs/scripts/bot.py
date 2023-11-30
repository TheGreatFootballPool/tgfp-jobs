"""This example requires the 'message_content' intent."""
import asyncio
import datetime
from contextlib import AsyncExitStack
from typing import List, Sequence, Optional

# pylint: disable=F0401
import discord
import arrow
import aiomqtt
from tgfp_lib import TGFP, TGFPGame, TGFPPlayer

from config import get_config

config = get_config()

NAG_CHANNEL = config.DISCORD_NAG_BOT_CHANNEL_ID


def get_first_game_of_the_week(tgfp: TGFP = None) -> TGFPGame:
    """ Returns the 'first' game of the week """
    if tgfp is None:
        tgfp = TGFP(config.MONGO_URI)
    games: List[TGFPGame] = tgfp.find_games(week_no=tgfp.current_week())
    games.sort(key=lambda x: x.start_time, reverse=True)
    return games[-1]


def get_nag_payload(members: Sequence[Member]) -> Optional[str]:
    """ Gets the embed message to send to the server """
    print("Getting nag payload")
    tgfp = TGFP(config.MONGO_URI)
    first_game: TGFPGame = get_first_game_of_the_week(tgfp)
    game_1_start = arrow.get(first_game.start_time)
    delta: datetime.timedelta = game_1_start - arrow.utcnow()
    kickoff_in_minutes: int = round(delta.seconds / 60)
    member: discord.Member
    late_players: List[TGFPPlayer] = []
    message: Optional[str] = None
    for member in members:
        if not member.bot:
            player: TGFPPlayer = tgfp.find_players(discord_id=member.id)[0]
            if player.active and not player.this_weeks_picks():
                late_players.append(player)

    if late_players:
        message = "This is the TGFP NagBot with a friendly reminder to the following:\n"
        for player in late_players:
            message += f"• <@{player.discord_id}>\n"
        message += "\nYou still need to enter your picks."
        message += " Go to https://tgfp.us/picks and get 'em in!"
        message += f"\nKickoff of first game is in {kickoff_in_minutes} minutes!"
    else:
        if config.ENVIRONMENT == 'development':
            message = "No players to nag"
    return message


class Bot(discord.Client):
    """ TGFP Bot """
    def __init__(self, *, mqtt_client, intents, **options) -> None:
        super().__init__(intents=intents, **options)
        self.mqtt_client: aiomqtt.Client = mqtt_client

    async def setup_hook(self) -> None:
        """ Setup hook """
        asyncio.create_task(self.subscriber())

    async def subscriber(self):
        """ Subscriber """
        await self.wait_until_ready()
        # noinspection PyTypeChecker
        await self.mqtt_client.subscribe("tgfp-bot/#")

        print("Started listening to messages from MQTT...")
        async with self.mqtt_client.messages() as messages:
            message: aiomqtt.client.Message
            async for message in messages:
                if message.topic.matches("tgfp-bot/nag-bot"):
                    channel: discord.TextChannel = self.get_channel(NAG_CHANNEL)
                    my_guild: discord.Guild = self.get_guild(config.DISCORD_GUILD_ID)
                    payload: Optional[str] = get_nag_payload(my_guild.members)
                    if payload:
                        await channel.send(payload)


async def main():
    """ Main method """
    token = config.DISCORD_AUTH_TOKEN

    async with AsyncExitStack() as astack:
        mqtt_client = await astack.enter_async_context(aiomqtt.Client(config.MQTT_HOST))
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        bot = await astack.enter_async_context(Bot(mqtt_client=mqtt_client, intents=intents))
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
