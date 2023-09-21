""" Script will check for players who have not done their picks and 'nag' @mention them """
import asyncio
import datetime
from typing import Optional, List
import logging
import arrow
import hikari
from prefect import flow, get_run_logger
from tgfp_lib import TGFP, TGFPPlayer, TGFPGame

from prefect_helpers import helpers


def get_first_game_of_the_week(tgfp: TGFP = None) -> TGFPGame:
    """ Returns the 'first' game of the week """
    if tgfp is None:
        mongo_uri: str = helpers.get_secret('mongo-uri')
        tgfp = TGFP(mongo_uri)
    games: List[TGFPGame] = tgfp.find_games(week_no=tgfp.current_week())
    games.sort(key=lambda x: x.start_time, reverse=True)
    return games[-1]


@flow
def nag_the_players():
    """ Nag the players that didn't do their picks """
    logger = get_run_logger()
    mongo_uri: str = helpers.get_secret('mongo-uri')
    discord_auth_token: str = helpers.get_secret('discord-auth-token', use_env=False)
    guid_name: str = helpers.get_secret('guild_name', is_var=True)

    bot: hikari.GatewayBot = hikari.GatewayBot(
        token=discord_auth_token,
        intents=hikari.Intents.ALL
    )

    @bot.listen(hikari.GuildAvailableEvent)
    async def guild_available(event: hikari.GuildAvailableEvent):
        """ Run when guild is available """
        tgfp = TGFP(mongo_uri)
        first_game: TGFPGame = get_first_game_of_the_week(tgfp)
        game_1_start = arrow.get(first_game.start_time)
        logger.info(game_1_start)
        logger.info(arrow.utcnow())
        delta: datetime.timedelta = game_1_start - arrow.utcnow()
        kickoff_in_minutes: int = round(delta.seconds / 60)

        if event.guild.name == guid_name:
            # first get the text channel handle
            text_channel: Optional[hikari.TextableChannel] = None
            channel: hikari.TextableChannel
            for _, channel in event.channels.items():
                if channel.name == 'nag-bot':
                    text_channel = channel
                    break

            member: hikari.guilds.Member
            late_players: List[TGFPPlayer] = []
            for _, member in event.members.items():
                if not member.is_bot:
                    player: TGFPPlayer = tgfp.find_players(discord_id=member.id)[0]
                    if player.active and not player.this_weeks_picks():
                        logger.info("Nagging %s", player.full_name())
                        late_players.append(player)

            if late_players:
                message = "This is the TGFP NagBot with a friendly reminder to the following:\n"
                for player in late_players:
                    message += f"• <@{player.discord_id}>\n"
                message += "\nYou still need to enter your picks."
                message += " Go to https://tgfp.us/picks and get 'em in!"
                message += f"\nKickoff of first game is in {kickoff_in_minutes} minutes!"
                await text_channel.send(content=message, user_mentions=True)
            await asyncio.sleep(2)
            await bot.close()

    logging.info("About to nag some players")
    bot.run()
