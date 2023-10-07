""" This is the file that will be loaded by the container """
from datetime import timedelta, datetime
from random import randrange
from typing import List

from prefect import flow, get_run_logger
from prefect.deployments import run_deployment
from tgfp_lib import TGFPGame

from nag_players import get_first_game_of_the_week
from update_game_score import this_weeks_games


@flow
def schedule_game_updates():
    """ Every week go get the games, and add the jobs to the scheduler for each game """
    logger = get_run_logger()
    games: List[TGFPGame] = this_weeks_games()
    jitter: int
    for game in games:
        jitter = randrange(1, 100)
        start_date: datetime = game.pacific_start_time - timedelta(seconds=jitter)
        log_msg: str = f"Adding game run flow: {game.tgfp_nfl_game_id} for time {start_date}"
        logger.info(log_msg)
        run_deployment(
            name="run-update-game/update-game-scores",
            scheduled_time=start_date,
            timeout=0,
            parameters={"tgfp_nfl_game_id": game.tgfp_nfl_game_id},
            flow_run_name=f"update-scores-game-{game.tgfp_nfl_game_id}"
        )


@flow
def schedule_player_nag():
    """ Creates the jobs to nag a player if they haven't done their picks"""
    logger = get_run_logger()
    first_game = get_first_game_of_the_week()
    logger.info(first_game.extra_info)
    scheduled_date: datetime = first_game.pacific_start_time
    run_deployment(
        name="nag-the-players/nag-all-players",
        scheduled_time=scheduled_date - timedelta(minutes=45),
        timeout=0,
        flow_run_name="nag-1"
    )
    run_deployment(
        name="nag-the-players/nag-all-players",
        scheduled_time=scheduled_date - timedelta(minutes=20),
        timeout=0,
        flow_run_name="nag-2"
    )
    run_deployment(
        name="nag-the-players/nag-all-players",
        scheduled_time=scheduled_date - timedelta(minutes=5),
        timeout=0,
        flow_run_name="nag-3"
    )
