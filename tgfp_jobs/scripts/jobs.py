""" This is the file that will be loaded by the container """
import logging
import os
import urllib.request
from typing import List
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
import paho.mqtt.client as mqtt

from tgfp_lib import TGFPGame

from db_backup import back_up_db
from picks_create import create_picks
from win_loss_update import this_weeks_games, update_win_loss
from players_nag import get_first_game_of_the_week, nag_players

SCHEDULE_DB_BACKUP_MINUTES: int = int(os.getenv('SCHEDULE_DB_BACKUP_MINUTES'))
SCHEDULE_HEALTH_CHECK_MINUTES: int = int(os.getenv('SCHEDULE_HEALTH_CHECK_MINUTES'))
SCHEDULE_START_DAY_OF_WEEK: str = os.getenv('SCHEDULE_START_DAY_OF_WEEK')
SCHEDULE_START_HOUR: int = int(os.getenv('SCHEDULE_START_HOUR'))
SCHEDULE_START_MINUTE: int = int(os.getenv('SCHEDULE_START_MINUTE'))
MQTT_HOST: str = os.getenv('MQTT_HOST')
# ENV variables
TZ: str = os.getenv('TZ')
LOG_LEVEL: str = os.getenv('LOG_LEVEL')
HEALTHCHECK_BASE_URL: str = os.getenv('HEALTHCHECK_BASE_URL')

logging.basicConfig(level=LOG_LEVEL)

scheduler: BackgroundScheduler = BackgroundScheduler()
scheduler.configure(timezone=TZ)


def on_message_create_picks(the_client, userdata, msg):
    """ mqtt message received """
    logging.info("Request to create picks page from MQTT")
    create_picks()
    ping_healthchecks(slug='create-picks-page')


def on_message_create_win_loss_schedule(the_client, userdata, msg):
    """ mqtt message received """
    logging.info("Request to create win / loss schedule from MQTT")
    create_update_win_loss_schedule()
    ping_healthchecks(slug='create-win-loss-schedule')


def on_message_create_nag_player_schedule(the_client, userdata, msg):
    """ mqtt message received """
    logging.info("Request to create nag player schedule from MQTT")
    create_nag_player_schedule()
    ping_healthchecks(slug='create-nag-player-schedule')


client = mqtt.Client('tgfp_job_server')
client.message_callback_add(
    'tgfp/create_picks',
    on_message_create_picks)
client.message_callback_add(
    'tgfp/create_win_loss_schedule',
    on_message_create_win_loss_schedule)
client.message_callback_add(
    'tgfp/create_nag_player_schedule',
    on_message_create_nag_player_schedule)

client.connect(MQTT_HOST, 1883)
client.subscribe('tgfp/#')


def ping_healthchecks(slug: str):
    """ Ping healthchecks """
    with urllib.request.urlopen(HEALTHCHECK_BASE_URL+slug, timeout=10) as response:
        logging.info(response.read())


def load_db_backup_schedule():
    """ Load the backup database schedule """
    ping_healthchecks(slug='backup-db')
    scheduler.add_job(
        run_backup_db,
        'interval',
        minutes=SCHEDULE_DB_BACKUP_MINUTES
    )


def load_week_start_schedule():
    """ Load the create picks page schedule """
    ping_healthchecks(slug='create-picks-page')
    scheduler.add_job(
        run_week_start,
        'cron',
        day_of_week=SCHEDULE_START_DAY_OF_WEEK,
        hour=SCHEDULE_START_HOUR,
        minute=SCHEDULE_START_MINUTE
    )


def load_all_jobs():
    """ Loads all the jobs """
    load_db_backup_schedule()
    load_week_start_schedule()


def run_backup_db():
    """Back up the database """
    back_up_db()
    ping_healthchecks(slug='backup-db')


def run_week_start():
    """ Gets the football pool ready for the week """
    # First we create the picks page which loads the current week schedule
    #   into the DB
    create_picks()
    ping_healthchecks(slug='create-picks-page')
    # Next, now that we have the games loaded, let's create the schedule
    #   for updating the win/loss/scores
    create_update_win_loss_schedule()
    ping_healthchecks(slug='create-win-loss-schedule')
    # Next, create the 'nag' schedule based on the first game
    create_nag_player_schedule()
    ping_healthchecks(slug='create-nag-player-schedule')


def run_update_win_loss(game: TGFPGame):
    """ Update scores / win / loss / standings """
    update_win_loss(game)


def run_nag_players():
    """ Nags the players re upcoming game """
    nag_players()
    ping_healthchecks(slug='nag-players')


def create_update_win_loss_schedule():
    """ Every week go get the games, and add the jobs to the scheduler for each game """
    games: List[TGFPGame] = this_weeks_games()
    for game in games:
        start_date: datetime = game.pacific_start_time
        end_date: datetime = start_date + timedelta(hours=4, minutes=15)
        log_msg: str = f"Adding game monitor: {game.tgfp_nfl_game_id} for time {start_date}"
        logging.info(log_msg)
        scheduler.add_job(
            run_update_win_loss,
            'interval',
            minutes=5,
            timezone=pytz.timezone(TZ),
            start_date=start_date,
            end_date=end_date,
            jitter=90,
            args=[game]
        )


def create_nag_player_schedule():
    """ Creates the jobs to nag a player if they haven't done their picks"""
    first_game = get_first_game_of_the_week()
    nag_date: datetime = first_game.pacific_start_time - timedelta(minutes=-45)
    scheduler.add_job(run_nag_players, 'date', run_date=nag_date)
    nag_date: datetime = first_game.pacific_start_time - timedelta(minutes=-20)
    scheduler.add_job(run_nag_players, 'date', run_date=nag_date)
    nag_date: datetime = first_game.pacific_start_time - timedelta(minutes=-5)
    scheduler.add_job(run_nag_players, 'date', run_date=nag_date)

if __name__ == "__main__":
    load_all_jobs()
    # Let's add a schedule to ping healthchecks as long as we're up
    scheduler.add_job(
        ping_healthchecks,
        'interval',
        minutes=SCHEDULE_HEALTH_CHECK_MINUTES,
        args=['job-runner']
    )
    ping_healthchecks(slug='job-runner')
    scheduler.start()
    try:
        client.loop_forever()
        # start the mqtt listener
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()
        client.loop_stop()
        client.disconnect()
