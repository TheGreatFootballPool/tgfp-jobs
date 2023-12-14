""" Sample discord bot """
from typing import List
from datetime import datetime

import pytz
from tgfp_nfl import TgfpNfl, TgfpNflGame

# pylint: disable=F0401
from config import get_config
import discord
from discord.ext import commands
from tgfp_lib import TGFP, TGFPGame, TGFPTeam

config = get_config()


class GameView(discord.ui.View):
    answer = None
    tgfp: TGFP = TGFP(config.MONGO_URI)

    @discord.ui.select(
        placeholder="What game do you want to analyze"
    )
    async def select_game(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        self.answer = select_item.values[0]
        await interaction.response.send_message(embed=self.get_embed(self.answer))  # noqa

    def set_options(self):
        options: List[discord.SelectOption] = []
        game: TGFPGame

        index: int = 1
        for game in self.tgfp.find_games(week_no=self.tgfp.current_week()):
            kickoff: str = game.pacific_start_time.strftime("%a, %d %b %Y %I:%M%p")
            options.append(
                discord.SelectOption(
                    label=game.extra_info['description'],
                    description=f"Kickoff: {kickoff} (Pacific Time)",
                    value=game.tgfp_nfl_game_id
                )
            )
            index += 1
        if len(options) == 0:
            options.append(
                discord.SelectOption(
                    label="Picks page not ready yet",
                    value="0"
                )
            )
        self.select_game.options = options

    def get_embed(self, tgfp_nfl_game_id: str) -> discord.Embed:
        tgfp_game: TGFPGame = self.tgfp.find_games(tgfp_nfl_game_id=tgfp_nfl_game_id)[0]
        utc_time: datetime = tgfp_game.start_time.replace(tzinfo=pytz.UTC)
        timestamp = int(datetime.timestamp(utc_time))
        favorite_team: TGFPTeam = self.tgfp.find_teams(tgfp_game.favorite_team_id)[0]
        espn_nfl: TgfpNfl = TgfpNfl(self.tgfp.current_week())
        espn_game: TgfpNflGame = espn_nfl.find_game(tgfp_game.tgfp_nfl_game_id)
        predicted_pt_diff, predicted_winner = espn_game.predicted_winning_diff_team
        description_header: str = ("Below is some data to help you make a decision.\n  "
                                   "You can compare the vegas betting line against ESPNs "
                                   "predicted score\n"
                                   "\n"
                                   "**FPI**:\n"
                                   "> Football Power Index that measures team's true strength on "
                                   "net points scale; expected point margin vs average opponent on "
                                   "neutral field.")

        embed = discord.Embed(title=tgfp_game.extra_info['description'],
                              description=f"{description_header}\n\n"
                                          "**__TGFP Game Info__**\n"
                                          f"> **Kickoff**: <t:{timestamp}:F>\n"
                                          f"> **Favorite**: {favorite_team.long_name} by "
                                          f"{tgfp_game.spread}\n"
                                          "**\n__ESPN Game Matchup Info__**\n"
                                          f"> **ESPN Prediction**: {predicted_winner.long_name} by "
                                          f"{predicted_pt_diff}\n"
                                          f"> **{espn_game.home_team.long_name} FPI**: "
                                          f"{espn_game.home_team_fpi}\n"
                                          f"> **{espn_game.away_team.long_name} FPI**: "
                                          f"{espn_game.away_team_fpi}\n"
                                          f"> **{espn_game.home_team.long_name} Win %**: "
                                          f"{espn_game.home_team_predicted_win_pct}\n"
                                          f"> **{espn_game.away_team.long_name} Win %**: "
                                          f"{espn_game.away_team_predicted_win_pct}\n",
                                          # f"> **NFL Game ID**: {espn_game.event_id}\n"
                              colour=0x00b0f4
                              )

        # embed.set_image(url="https://cubedhuang.com/images/alex-knight-unsplash.webp")
        #
        # embed.set_thumbnail(url="https://dan.onl/images/emptysong.jpg")
        #
        # embed.set_footer(text="ESPN Event ID",
        #                  icon_url="https://slate.dan.onl/slate.png")
        return embed


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
    async def game(ctx):
        view = GameView()
        view.set_options()
        await ctx.send(view=view)

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
