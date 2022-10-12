""" Used to create the picks page """
import os
import urllib.request
import pprint
import logging
from typing import List
import sentry_sdk
from tgfp_lib import TGFP, TGFPGame
from tgfp_nfl import TgfpNfl


class CreatePicksException(Exception):
    """ Exception class """
    def __init__(self, msg, *args):
        super().__init__(args)
        self.msg = msg

    def __str__(self):
        return f"Exception: {self.msg}"


pp = pprint.PrettyPrinter(indent=4)

HEALTHCHECK_URL = os.getenv('HEALTHCHECK_URL') + 'create-picks-page'


def create_picks():
    """ Runs the main method to create the picks page """
    tgfp = TGFP()
    tgfp_teams = tgfp.teams()
    week_no = tgfp.current_week()
    nfl = TgfpNfl(week_no=week_no)
    nfl_games = nfl.games()
    logging.info("Current week: %d", week_no)
    if not nfl_games:
        logging.error("Create Picks had an exception")
        raise CreatePicksException("There should have been games!!!")
    all_json: List = []
    for nfl_game in nfl_games:
        logging.info("nfl_game_id: %d", nfl_game.id)
        logging.info(nfl_game.away_team.full_name)
        road_team_id = nfl_game.away_team.tgfp_id(tgfp_teams)
        home_team_id = nfl_game.home_team.tgfp_id(tgfp_teams)
        fav_team_id = nfl_game.favored_team.tgfp_id(tgfp_teams)
        logging.info("road_team_id: %s", str(road_team_id))
        logging.info(nfl_game.home_team.full_name)
        logging.info("home_team_id: %s", str(home_team_id))
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
        logging.info("Saving game in mongo database")
        all_json.append(tgfp_game.mongo_data())
        logging.info(tgfp_game.mongo_data())
        tgfp_game.save()

    with urllib.request.urlopen(HEALTHCHECK_URL, timeout=10) as response:
        response_text = response.read()
        logging.info(response_text)


if __name__ == '__main__':

    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN_TGFP_BIN'),
        environment=os.getenv('SENTRY_ENVIRONMENT'),
        traces_sample_rate=1.0
    )

    create_picks()
