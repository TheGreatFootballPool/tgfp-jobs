""" Sample discord bot """
# pylint: disable=F0401
from typing import List, Tuple, Optional
from datetime import datetime

from donut import get_matchup_chart
import pytz
from tgfp_nfl import TgfpNfl, TgfpNflGame

from config import get_config
import discord
from discord.ext import commands
from discord import app_commands
from tgfp_lib import TGFP, TGFPGame, TGFPTeam

config = get_config()


class GameCommand:
    """ Holds all the information for the game pick command """
    def __init__(self):
        self.tgfp: TGFP = TGFP(config.MONGO_URI)
        self._games_values: Optional[Tuple[List, List]] = None

    @property
    def games_values(self) -> Tuple[List, List]:
        """ Get all games and values for the week """
        if self._games_values is None:
            games: List = []
            values: List = []
            for game in self.tgfp.find_games(week_no=self.tgfp.current_week()):
                if game.is_pregame:
                    games.append(game.extra_info['description'])
                    values.append(game.tgfp_nfl_game_id)
            self._games_values = games, values

        return self._games_values

    def get_embed(self, tgfp_nfl_game_id: str) -> Tuple[discord.Embed, discord.File]:
        tgfp_game: TGFPGame = self.tgfp.find_games(tgfp_nfl_game_id=tgfp_nfl_game_id)[0]
        utc_time: datetime = tgfp_game.start_time.replace(tzinfo=pytz.UTC)
        timestamp = int(datetime.timestamp(utc_time))
        favorite_team: TGFPTeam = self.tgfp.find_teams(tgfp_game.favorite_team_id)[0]
        espn_nfl: TgfpNfl = TgfpNfl(self.tgfp.current_week())
        espn_game: TgfpNflGame = espn_nfl.find_game(nfl_game_id=tgfp_game.tgfp_nfl_game_id)
        predicted_pt_diff, predicted_winner = espn_game.predicted_winning_diff_team
        home_color: str = espn_game.home_team.color
        if espn_game.favored_team:
            home_color = espn_game.favored_team.color
        description_header: str = ('Below is some data to help you make a decision.\n  '
                                   'You can compare the vegas betting line against ESPNs '
                                   'predicted score\n'
                                   '> **Warning**: From what I can tell the ESPN predicted'
                                   ' score does not take into account injuries.'
                                   '\n'
                                   '**FPI**:\n'
                                   '> Football Power Index that measures team\'s true strength on '
                                   'net points scale; expected point margin vs average opponent on '
                                   'neutral field.')

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
                                          f"{espn_game.away_team_fpi}\n",
                              colour=discord.Colour.from_str(f"#{home_color}")
                              )
        filename = get_matchup_chart(espn_game)
        file = discord.File(filename)
        embed.set_image(url=f"attachment://{filename}")
        #
        # embed.set_thumbnail(url="https://dan.onl/images/emptysong.jpg")
        #
        # embed.set_footer(text="ESPN Event ID",
        #                  icon_url="https://slate.dan.onl/slate.png")
        return embed, file

    def reset(self):
        self._games_values = None


def run():
    """ Run the bot """
    intents = discord.Intents.all()

    bot = commands.Bot(command_prefix="!", intents=intents)
    guild_id: discord.Object = discord.Object(id=config.DISCORD_GUILD_ID)
    game_command: GameCommand = GameCommand()

    @bot.event
    async def on_ready():
        print(f"User: {bot.user} (ID: {bot.user.id})")

        bot.tree.copy_global_to(guild=guild_id)
        await bot.tree.sync(guild=guild_id)

    async def game_autocomplete(
            _: discord.Interaction,
            current: str
    ) -> List[app_commands.Choice[str]]:
        data = []
        games, values = game_command.games_values
        for index, game_choice in enumerate(games):
            if current.lower() in game_choice.lower():
                data.append(app_commands.Choice(name=games[index], value=values[index]))
        return data

    @bot.tree.command()
    @app_commands.autocomplete(picked_game=game_autocomplete)
    async def game(interaction: discord.Interaction, picked_game: str):
        game_command.reset()
        await interaction.response.defer(thinking=True, ephemeral=True)  # noqa
        embed, file = game_command.get_embed(picked_game)
        await interaction.followup.send(embed=embed, file=file)  # noqa

    bot.run(token=config.DISCORD_AUTH_TOKEN)


if __name__ == '__main__':
    run()
