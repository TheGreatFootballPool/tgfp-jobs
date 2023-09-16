""" This is the file that will be loaded by the container """
import os
from datetime import timedelta
from prefect import flow, get_run_logger, variables, serve
from prefect.blocks.system import Secret
from prefect.client.schemas.schedules import IntervalSchedule, CronSchedule

from tgfp_lib import TGFPGame

from db_backup import back_up_db
from picks_create import create_picks
# from win_loss_update import this_weeks_games, update_win_loss
# from players_nag import get_first_game_of_the_week, nag_players

ENV: str = os.getenv('ENVIRONMENT')


def get_secret(secret_name: str, is_var: bool = False, use_env: bool = True) -> str:
    """ Retrieves the secret or variable, using the current environment """
    secret_string: str
    env_string: str = ENV if use_env else ""
    if is_var:
        return str(variables.get(f"{secret_name}_{env_string}"))
    with Secret.load(f"{secret_name}-{env_string}") as a_secret:
        secret_string = a_secret.get()
    return secret_string

TZ: str = os.getenv('TZ')


#
# def load_all_jobs():
#     """ Loads all the jobs """
#     load_db_backup_schedule()
#     load_week_start_schedule()
@flow()
def run_backup_db():
    """Back up the database """
    logger = get_run_logger()
    logger.info("Backing up database")
    back_up_db()


@flow()
def run_begin_week():
    """ Gets the football pool ready for the week """
    # First we create the picks page which loads the current week schedule
    #   into the DB
    create_picks()
    # # Next, now that we have the games loaded, let's create the schedule
    # #   for updating the win/loss/scores
    # create_update_win_loss_schedule()
    # ping_healthchecks(slug='create-win-loss-schedule')
    # # Next, create the 'nag' schedule based on the first game
    # create_nag_player_schedule()
    # ping_healthchecks(slug='create-nag-player-schedule')


def run_update_win_loss(game: TGFPGame):
    """ Update scores / win / loss / standings """
    update_win_loss(game)


def run_nag_players():
    """ Nags the players re upcoming game """
    nag_players()


# def create_update_win_loss_schedule():
#     """ Every week go get the games, and add the jobs to the scheduler for each game """
#     games: List[TGFPGame] = this_weeks_games()
#     for game in games:
#         start_date: datetime = game.pacific_start_time
#         end_date: datetime = start_date + timedelta(hours=4, minutes=15)
#         log_msg: str = f"Adding game monitor: {game.tgfp_nfl_game_id} for time {start_date}"
#         logging.info(log_msg)
# scheduler.add_job(
#     run_update_win_loss,
#     'interval',
#     minutes=5,
#     timezone=pytz.timezone(TZ),
#     start_date=start_date,
#     end_date=end_date,
#     jitter=90,
#     args=[game]
# )


# def create_nag_player_schedule():
#     """ Creates the jobs to nag a player if they haven't done their picks"""
    # first_game = get_first_game_of_the_week()
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
        name="Back up DB",
        description="Backs up the TGFP Database regularly",
        version="0.2"
    )
    # Create 'begin week' deployment
    begin_week_deploy = run_begin_week.to_deployment(
        schedule=CronSchedule(cron="0 6 * * 1", timezone=TZ),
        name="Begin the Week",
        description="Creates the picks page, and triggers scheduling of games",
        version="0.1"
    )
    serve(
        backup_db_deploy,
        begin_week_deploy
    )
    # load_all_jobs()
    # # Let's add a schedule to ping healthchecks as long as we're up
    # scheduler.add_job(
    #     ping_healthchecks,
    #     'interval',
    #     minutes=SCHEDULE_HEALTH_CHECK_MINUTES,
    #     args=['job-runner']
    # )
    # ping_healthchecks(slug='job-runner')
    # scheduler.start()
    # try:
    #     client.loop_forever()
    #     # start the mqtt listener
    # except (KeyboardInterrupt, SystemExit):
    #     pass
    # finally:
    #     scheduler.shutdown()
    #     client.loop_stop()
    #     client.disconnect()
