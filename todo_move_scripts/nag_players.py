""" Script will check for players who have not done their picks and 'nag' @mention them """
import asyncio
import datetime
import os
from typing import Optional, List

import arrow

import hikari
from tgfp_lib import TGFP, TGFPPlayer, TGFPGame

bot: hikari.GatewayBot = hikari.GatewayBot(
    token=os.getenv('DISCORD_AUTH_TOKEN'),
    intents=hikari.Intents.ALL
)


@bot.listen(hikari.GuildAvailableEvent)
async def guild_available(event: hikari.GuildAvailableEvent):
    tgfp = TGFP()

    game: TGFPGame
    games: List[TGFPGame] = tgfp.find_games(week_no=tgfp.current_week())
    games.sort(key=lambda x: x.start_time, reverse=True)
    game_1_start = arrow.get(games[-1].start_time)
    print(game_1_start)
    print(arrow.utcnow())
    delta: datetime.timedelta = game_1_start - arrow.utcnow()
    kickoff_in_minutes: int = round(delta.seconds / 60)

    if event.guild.name == 'The Great Football Pool':
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
                    late_players.append(player)

        if late_players:
            message = "This is the TGFP NagBot with a friendly reminder to the following:\n"
            for player in late_players:
                message += f"• <@{player.discord_id}>\n"
            message += "\nYou still need to enter your picks.  Go to https://tgfp.us/picks and get 'em in!"
            message += f"\nKickoff of first game is in {kickoff_in_minutes} minutes!"
            await text_channel.send(content=message, user_mentions=True)
        await asyncio.sleep(2)
        await bot.close()


def nag_players():
    bot.run()

if __name__ == '__main__':
    nag_players()