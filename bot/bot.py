""" Script will listen for messages and respond with smart things """
import os
import urllib.request
import logging
import sentry_sdk
import hikari
import lightbulb
from lightbulb.ext import tasks
from tgfp_lib import TGFP, TGFPPlayer
from scripts import get_help, get_game_care_scores_for_player, formatted_care, pick_detail_embed

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN_TGFP_BOT'),
    environment=os.getenv('SENTRY_ENVIRONMENT'),
    traces_sample_rate=1.0
)
bot: lightbulb.BotApp = lightbulb.BotApp(
    token=os.getenv('DISCORD_AUTH_TOKEN'),
    intents=hikari.Intents.ALL,
    banner=None
)
tasks.load(bot)

HEALTHCHECK_URL = os.getenv('HEALTHCHECK_URL') + 'tgfp-bot'


@bot.command
@lightbulb.option(
    "expand",
    description="display results in expanded form, more detail",
    type=bool,
    default=False
)
@lightbulb.command("do_i_care", description="How much do you care about this week's games")
@lightbulb.implements(lightbulb.SlashCommand)
async def do_i_care(ctx: lightbulb.Context) -> None:
    """ Answers the question. do I really care?"""
    tgfp: TGFP = TGFP()
    player: TGFPPlayer = tgfp.find_players(discord_id=ctx.member.id)[0]
    if not player.this_weeks_picks():
        await ctx.respond("You must not care that much, you haven't even entered your picks yet!")
    else:
        scores = get_game_care_scores_for_player(tgfp=tgfp, player=player)
        await ctx.respond(formatted_care(tgfp=tgfp, care_scores=scores))


@bot.command
@lightbulb.option(
    "help_topic",
    description="Get help for the various TGFP Bot commands",
    choices=['all', 'do_i_care', 'pick_detail']
)
@lightbulb.command("help", description="TGFP Bot Command Help")
@lightbulb.implements(lightbulb.SlashCommand)
async def give_help(ctx: lightbulb.Context) -> None:
    """ Provides help for slash commands """
    match ctx.options.help_topic:
        case 'do_i_care':
            await ctx.respond(get_help('do_i_care'))
        case 'pick_detail':
            await ctx.respond(get_help('pick_detail'))
        case 'all':
            await ctx.respond(get_help('all'))


@bot.command
@lightbulb.command("pick_detail", description="Gives a detailed report of your picks for the week")
@lightbulb.implements(lightbulb.SlashCommand)
async def pick_detail(ctx: lightbulb.Context) -> None:
    """ Gives very detailed picks """
    tgfp: TGFP = TGFP()
    player: TGFPPlayer = tgfp.find_players(discord_id=ctx.member.id)[0]
    if not player.this_weeks_picks():
        await ctx.respond("You must not care that much, you haven't even entered your picks yet!")
    else:
        scores = get_game_care_scores_for_player(player, tgfp)
        await ctx.respond(pick_detail_embed(scores, tgfp))


@tasks.task(m=15)
async def ping_healthchecks():
    """ Ping healthchecks"""
    logging.info("About to ping healthchecks")
    with urllib.request.urlopen(HEALTHCHECK_URL, timeout=10) as response:
        logging.info(response.read())


def main():
    """ Main function """
    with urllib.request.urlopen(HEALTHCHECK_URL, timeout=10) as response:
        logging.info(response.read())
    ping_healthchecks.start()
    bot.run()


if __name__ == '__main__':
    main()
