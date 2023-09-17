""" This is the file that will be loaded by the container """
import os
from datetime import timedelta, datetime
from random import randrange
from time import sleep
from typing import List

from prefect import flow, get_run_logger, serve
from prefect.client.schemas.schedules import IntervalSchedule, CronSchedule
from prefect.deployments import run_deployment
from tgfp_lib import TGFPGame

from db_backup import back_up_db
from picks_create import create_picks
# from win_loss_update import this_weeks_games, update_win_loss
from players_nag import nag_players, get_first_game_of_the_week
from scripts.win_loss_update import update_win_loss, this_weeks_games

ENV: str = os.getenv('ENVIRONMENT')
TZ: str = os.getenv('TZ')


@flow(name="backup-db")
def run_backup_db():
    """Back up the database """
    logger = get_run_logger()
    logger.info("Backing up database")
    back_up_db()


@flow(name="begin-week")
def run_begin_week(skip_create_picks: bool = False):
    """ Create the picks page, and schedule pause / resume jobs """
    if skip_create_picks is False:
        create_picks()
    create_update_win_loss_schedule()


@flow(name="win-loss-update")
def run_update_win_loss(tgfp_nfl_game_id: str):
    """ Update scores / win / loss / standings """
    logger = get_run_logger()
    game_is_final: bool = False
    while True:
        logger.info("Updating game")
        game_is_final = update_win_loss(tgfp_nfl_game_id)
        if game_is_final:
            break
        sleep(300)
    logger.info("Got a final for the game, exiting run flow")


@flow(name="nag-players")
def run_nag_players():
    """ Nags the players re upcoming game """
    nag_players()


@flow(name="schedule-game-updates")
def create_update_win_loss_schedule():
    """ Every week go get the games, and add the jobs to the scheduler for each game """
    logger = get_run_logger()
    games: List[TGFPGame] = this_weeks_games()
    jitter: int = randrange(1, 100)
    for game in games:
        jitter = randrange(1, 100)
        start_date: datetime = (game.pacific_start_time - timedelta(seconds=jitter))
        log_msg: str = f"Adding game run flow: {game.tgfp_nfl_game_id} for time {start_date}"
        logger.info(log_msg)
        run_deployment(
            name="win-loss-update/update",
            scheduled_time=start_date,
            timeout=0,
            parameters={"tgfp_nfl_game_id": game.tgfp_nfl_game_id},
            flow_run_name=f"update-scores-game-{game.tgfp_nfl_game_id}"
        )


@flow(name="create-nag-player-schedule")
def create_nag_player_schedule():
    """ Creates the jobs to nag a player if they haven't done their picks"""
    logger = get_run_logger()
    first_game = get_first_game_of_the_week()
    logger.info(first_game.extra_info)
    # run_depl
    # nag_date: datetime = first_game.pacific_start_time - timedelta(minutes=-45)
    # scheduler.add_job(run_nag_players, 'date', run_date=nag_date)
    # nag_date: datetime = first_game.pacific_start_time - timedelta(minutes=-20)
    # scheduler.add_job(run_nag_players, 'date', run_date=nag_date)
    # nag_date: datetime = first_game.pacific_start_time - timedelta(minutes=-5)
    # scheduler.add_job(run_nag_players, 'date', run_date=nag_date)


if __name__ == "__main__":
    # Create backup job deployment
    backup_db_deploy = run_backup_db.to_deployment(
        schedule=IntervalSchedule(interval=timedelta(minutes=30), timezone=TZ),
        name="backup",
        description="Backs up the TGFP Database regularly",
        version="0.4"
    )
    begin_week_deploy = run_begin_week.to_deployment(
        schedule=CronSchedule(cron="0 6 * * 3", timezone=TZ),
        name="begin-week",
        description="Creates the picks page, and triggers scheduling of games",
        version="0.3"
    )
    nag_players_deploy = run_nag_players.to_deployment(
        name="nag",
        description="Nag the players in the football pool to enter their picks",
        version="0.2"
    )
    update_win_loss_deploy = run_update_win_loss.to_deployment(
        name="update",
        description="Updates the scores and win/loss records",
        version="0.3"
    )
    create_update_win_loss_schedule_deploy = create_update_win_loss_schedule.to_deployment(
        name="schedule-update-flows",
        description="Run manually to create the win/loss update schedule for the week",
        version="1.0"
    )
    serve(
        backup_db_deploy,
        begin_week_deploy,
        nag_players_deploy,
        update_win_loss_deploy,
        create_update_win_loss_schedule_deploy
    )
