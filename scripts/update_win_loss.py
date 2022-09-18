""" This file will update all the scores in the mongo DB for the great football pool """
import socket
import urllib.request
import pprint
from typing import List
import logging
from tgfp_lib import TGFP, TGFPGame
from tgfp_nfl import TgfpNfl


def update_win_loss():
    try:
        urllib.request.urlopen("https://hc-ping.com/26764645-4b82-4002-af99-48cb34b07b2f", timeout=10)
    except socket.error as e:
        # Log ping failure here...
        print("Ping failed: %s" % e)
    logger = logging.getLogger('win_loss_logger')

    logging.basicConfig(
        filename='/var/log/update_win_loss.log',
        filemode='w',
        format='%(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

    tgfp = TGFP()
    week_no = tgfp.current_week()
    nfl_data_source = TgfpNfl(week_no=week_no)
    nfl_game = nfl_data_source.games()[0]
    games: List[TGFPGame] = tgfp.find_games(tgfp_nfl_game_id=nfl_game.id)
    if not games:
        logger.warning(
            f'''No games yet, this happens if you haven't created the picks page for the current week
Current week is: {tgfp.current_week()}'''
        )
        return
    update_scores(tgfp, nfl_data_source, logger=logger)
    update_player_win_loss(tgfp, logger=logger)
    update_team_records(tgfp, nfl_data_source)


def update_scores(tgfp, nfl_data_source, logger: logging.Logger):
    """ This is the function runs the entire module. """
    pretty_printer = pprint.PrettyPrinter(indent=4)
    nfl_games = nfl_data_source.games()
    all_games_are_final = True

    for nfl_game in nfl_games:
        tgfp_g: TGFPGame = tgfp.find_games(tgfp_nfl_game_id=nfl_game.id)[0]
        if not nfl_game.is_pregame:
            logger.info("Games are in progress")
            if tgfp_g:
                if tgfp_g.home_team_score != int(nfl_game.total_home_points) or \
                   tgfp_g.road_team_score != int(nfl_game.total_away_points) or \
                   tgfp_g.game_status != nfl_game.game_status_type:
                    tgfp_g.home_team_score = int(nfl_game.total_home_points)
                    tgfp_g.road_team_score = int(nfl_game.total_away_points)
                    tgfp_g.game_status = nfl_game.game_status_type
                    logger.info("saving a game score")
                if nfl_game.is_final:
                    logger.info("Score is final")

        tgfp_g.save()

        if not nfl_game.is_final:
            all_games_are_final = False

    if all_games_are_final:
        logger.info("all games are final")


def update_player_win_loss(tgfp, logger: logging.Logger):
    """ Main function for running the entire file """

    active_players = tgfp.find_players(player_active=True)

    for player in active_players:
        logger.info("Working on %s" % player.nick_name)
        picks = tgfp.find_picks(player_id=player.id)
        for pick in picks:
            pick.load_record()
            pick.save()


def update_team_records(tgfp, nfl_data_source):
    for nfl_team in nfl_data_source.teams():
        tgfp_team = tgfp.find_teams(tgfp_nfl_team_id=nfl_team.id)[0]
        tgfp_team.wins = nfl_team.wins
        tgfp_team.losses = nfl_team.losses
        tgfp_team.ties = nfl_team.ties
        tgfp_team.logo_url = nfl_team.logo_url
        tgfp_team.save()
