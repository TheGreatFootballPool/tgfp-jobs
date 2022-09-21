""" Used to create the picks page """
import urllib.request
import pprint
import logging
from typing import List

from tgfp_lib import TGFP, TGFPGame
from tgfp_nfl import TgfpNfl

pp = pprint.PrettyPrinter(indent=4)
tgfp = TGFP()
tgfp_teams = tgfp.teams()
week_no = tgfp.current_week()
nfl = TgfpNfl(week_no=week_no)
nfl_games = nfl.games()


def round_to(number, precision):
    """ rounds a given number to a given precision """
    correction = 0.5 if number >= 0 else -0.5
    return int(number / precision + correction) * precision


def create_picks():
    """ Runs the main method to create the picks page """
    urllib.request.urlopen(
        "https://hc-ping.com/ae09aed7-ec22-47f6-9e1a-67ab5421aec3",
        timeout=10
    )
    logging.info("Current week: %d" % week_no)
    all_json: List = []
    for nfl_game in nfl_games:
        logging.info("nfl_game_id: " + nfl_game.id)
        logging.info(nfl_game.away_team.full_name)
        road_team_id = nfl_game.away_team.tgfp_id(tgfp_teams)
        home_team_id = nfl_game.home_team.tgfp_id(tgfp_teams)
        fav_team_id = nfl_game.favored_team.tgfp_id(tgfp_teams)
        logging.info("road_team_id: " + str(road_team_id))
        logging.info(nfl_game.home_team.full_name)
        logging.info("home_team_id: " + str(home_team_id))
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

if __name__ == '__main__':
    create_picks()
