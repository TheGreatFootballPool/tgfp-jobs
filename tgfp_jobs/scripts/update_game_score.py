""" Take a game, and get the current scores from TgfpNfl and update the TGFP game """
from time import sleep
from typing import List

from prefect import flow, get_run_logger
from tgfp_lib import TGFP, TGFPGame
from tgfp_nfl import TgfpNfl

from config import get_config

config = get_config()

class UpdateWinLossException(Exception):
    """ Throw an exception """
    def __init__(self, msg, *args):
        super().__init__(args)
        self.msg = msg

    def __str__(self):
        return f"Exception: {self.msg}"


@flow(flow_run_name="update-game-{tgfp_nfl_game_id}")
def run_update_game(tgfp_nfl_game_id: str):
    """ Update scores / win / loss / standings """
    logger = get_run_logger()
    game_is_final: bool = update_game(tgfp_nfl_game_id)
    while not game_is_final:
        logger.info("Updating game")
        sleep(300)
        game_is_final = update_game(tgfp_nfl_game_id)
    logger.info("Got a final for the game, exiting run flow")


def update_game(tgfp_nfl_game_id: str) -> bool:
    """
    Update all the wins / losses / scores, etc...
    @param tgfp_nfl_game_id:
    @return: True if game is final, otherwise False
    """

    tgfp = TGFP(config.MONGO_URI)
    week_no = tgfp.current_week()
    nfl_data_source = TgfpNfl(week_no=week_no)
    games: List[TGFPGame] = tgfp.find_games(tgfp_nfl_game_id=tgfp_nfl_game_id)
    if len(games) != 1:
        raise UpdateWinLossException(f"We should have found a game for id {tgfp_nfl_game_id}")

    tgfp_game = games[0]
    game_is_final: bool = _update_scores(nfl_data_source, tgfp_game)
    _update_player_win_loss(tgfp)
    _update_team_records(tgfp, nfl_data_source)
    return game_is_final


def _update_scores(nfl_data_source, tgfp_game: TGFPGame) -> bool:
    """
    Update the tgfp_game with the data from the nfl data source
    @param nfl_data_source: current nfl game day data
    @param tgfp_game: game to update
    @return: True if game is final, otherwise, false
    """
    nfl_game = nfl_data_source.find_game(game_id=tgfp_game.tgfp_nfl_game_id)
    if not nfl_game.is_pregame:
        if tgfp_game.home_team_score != int(nfl_game.total_home_points) or \
           tgfp_game.road_team_score != int(nfl_game.total_away_points) or \
           tgfp_game.game_status != nfl_game.game_status_type:
            tgfp_game.home_team_score = int(nfl_game.total_home_points)
            tgfp_game.road_team_score = int(nfl_game.total_away_points)
            tgfp_game.game_status = nfl_game.game_status_type

    tgfp_game.save()
    logger = get_run_logger()
    log_msg = f"Game state: {tgfp_game.game_status}"
    logger.info(log_msg)
    return tgfp_game.is_final


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
    tgfp = TGFP(config.MONGO_URI)
    return tgfp.find_games(
        week_no=tgfp.current_week(),
        season=tgfp.current_season()
    )
