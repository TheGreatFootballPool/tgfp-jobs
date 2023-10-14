""" Used to create the picks page """
from typing import List

from prefect import get_run_logger, flow
from tgfp_lib import TGFP, TGFPGame
from tgfp_nfl import TgfpNfl

from config import get_config
from send_picks_ready_campaign import send_campaign_email
config = get_config()


class CreatePicksException(Exception):
    """ Exception class """
    def __init__(self, msg, *args):
        super().__init__(args)
        self.msg = msg

    def __str__(self):
        return f"Exception: {self.msg}"


@flow
def create_picks():
    """ Creates the weekly picks page """
    logger = get_run_logger()
    mongo_uri = config.MONGO_URI
    tgfp = TGFP(mongo_uri)
    tgfp_teams = tgfp.teams()
    week_no = tgfp.current_week()
    nfl = TgfpNfl(week_no=week_no)
    nfl_games = nfl.games()
    logger.info("Current week: %d", week_no)
    if not nfl_games:
        logger.error("Create Picks had an exception")
        raise CreatePicksException("There should have been games!!!")
    all_json: List = []
    for nfl_game in nfl_games:
        logger.info("nfl_game_id: %s", nfl_game.id)
        logger.info(nfl_game.away_team.full_name)
        road_team_id = nfl_game.away_team.tgfp_id(tgfp_teams)
        home_team_id = nfl_game.home_team.tgfp_id(tgfp_teams)
        fav_team_id = nfl_game.favored_team.tgfp_id(tgfp_teams)
        logger.info("road_team_id: %s", str(road_team_id))
        logger.info(nfl_game.home_team.full_name)
        logger.info("home_team_id: %s", str(home_team_id))
        tgfp_game = TGFPGame(tgfp=tgfp)
        tgfp_game.favorite_team_id = fav_team_id
        tgfp_game.game_status = nfl_game.game_status_type
        tgfp_game.home_team_id = home_team_id
        tgfp_game.home_team_score = 0
        tgfp_game.road_team_id = road_team_id
        tgfp_game.road_team_score = 0
        tgfp_game.spread = nfl_game.spread
        tgfp_game.start_time = nfl_game.start_time
        tgfp_game.week_no = int(week_no)
        tgfp_game.tgfp_nfl_game_id = nfl_game.id
        tgfp_game.season = tgfp.current_season()
        tgfp_game.extra_info = nfl_game.extra_info
        logger.info("Saving game in mongo database")
        all_json.append(tgfp_game.mongo_data())
        logger.info(tgfp_game.mongo_data())
        tgfp_game.save()

    send_campaign_email(week_no)
