""" This file will update all the scores in the mongo DB for the great football pool """
import os
from typing import List
import urllib.request
import logging
from tgfp_lib import TGFP, TGFPGame
from tgfp_nfl import TgfpNfl

HEALTHCHECK_URL = os.getenv('HEALTHCHECK_BASE_URL') + 'update-win-loss-scores'
MONGO_URI = os.getenv('MONGO_URI')
TZ = os.getenv('TZ')


class UpdateWinLossException(Exception):
    """ Throw an exception """
    def __init__(self, msg, *args):
        super().__init__(args)
        self.msg = msg

    def __str__(self):
        return f"Exception: {self.msg}"


def update_win_loss(tgfp_game: TGFPGame):
    """ Update all the wins """
    tgfp = TGFP(MONGO_URI)
    logging.basicConfig(level=logging.INFO)
    week_no = tgfp.current_week()
    nfl_data_source = TgfpNfl(week_no=week_no)
    nfl_game = nfl_data_source.games()[0]
    games: List[TGFPGame] = tgfp.find_games(tgfp_nfl_game_id=nfl_game.id)
    if not games:
        logging.warning(
            "No games yet, this happens if you haven't created the picks \
            page for the current week Current week is: %s", tgfp.current_week())
    else:
        try:
            _update_scores(nfl_data_source, tgfp_game)
        except UpdateWinLossException as exception:
            logging.error(exception)
            return

    try:
        _update_player_win_loss(tgfp)
    except UpdateWinLossException as exception:
        logging.error(exception)
        return

    try:
        _update_team_records(tgfp, nfl_data_source)
    except UpdateWinLossException as exception:
        logging.error(exception)
        return
    with urllib.request.urlopen(HEALTHCHECK_URL, timeout=10) as response:
        logging.info(response.read())


def _update_scores(nfl_data_source, tgfp_game: TGFPGame):
    nfl_game = nfl_data_source.find_game(game_id=tgfp_game.tgfp_nfl_game_id)
    if not nfl_game.is_pregame:
        if tgfp_game.home_team_score != int(nfl_game.total_home_points) or \
           tgfp_game.road_team_score != int(nfl_game.total_away_points) or \
           tgfp_game.game_status != nfl_game.game_status_type:
            tgfp_game.home_team_score = int(nfl_game.total_home_points)
            tgfp_game.road_team_score = int(nfl_game.total_away_points)
            tgfp_game.game_status = nfl_game.game_status_type

    tgfp_game.save()


def _update_player_win_loss(tgfp):
    active_players = tgfp.find_players(player_active=True)

    for player in active_players:
        picks = tgfp.find_picks(player_id=player.id)
        for pick in picks:
            pick.load_record()
            pick.save()


def _update_team_records(tgfp, nfl_data_source):
    for nfl_team in nfl_data_source.teams():
        tgfp_team = tgfp.find_teams(tgfp_nfl_team_id=nfl_team.id)[0]
        tgfp_team.wins = nfl_team.wins
        tgfp_team.losses = nfl_team.losses
        tgfp_team.ties = nfl_team.ties
        tgfp_team.logo_url = nfl_team.logo_url
        tgfp_team.save()


#  Helper function
def this_weeks_games() -> List[TGFPGame]:
    """ Get this week's games """
    tgfp = TGFP(MONGO_URI)
    return tgfp.find_games(
        week_no=tgfp.current_week(),
        season=tgfp.current_season()
    )


if __name__ == '__main__':
    for game in this_weeks_games():
        update_win_loss(game)
