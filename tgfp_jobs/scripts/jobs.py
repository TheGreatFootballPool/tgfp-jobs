""" This is the file that will be loaded by the container """
import logging
import os
import urllib.request
from apscheduler.schedulers.blocking import BlockingScheduler

from db_backup import back_up_db

SCHEDULE_DB_BACKUP_MINUTES: int = 30
SCHEDULE_HEALTH_CHECK_MINUTES: int = 60

# ENV variables
TZ: str = os.getenv('TZ')
LOG_LEVEL: str = os.getenv('LOG_LEVEL')
HEALTHCHECK_BASE_URL: str = os.getenv('HEALTHCHECK_BASE_URL')

logging.basicConfig(level=LOG_LEVEL)

scheduler = BlockingScheduler()
scheduler.configure(timezone=TZ)


def ping_healthchecks(slug: str):
    """ Ping healthchecks """
    with urllib.request.urlopen(HEALTHCHECK_BASE_URL+slug, timeout=10) as response:
        logging.info(response.read())


def load_db_backup_schedule():
    """ Load the backup database schedule """
    ping_healthchecks('backup-db')  # Ping once. We're UP!
    scheduler.add_job(run_backup_db, 'interval', minutes=SCHEDULE_DB_BACKUP_MINUTES)


def load_healthcheck_schedule():
    """ Load the healthchecks schedule """
    ping_healthchecks('job-runner')  # Ping once. We're UP!
    scheduler.add_job(
        ping_healthchecks,
        'interval',
        minutes=SCHEDULE_HEALTH_CHECK_MINUTES,
        args=['job-runner']
    )


def load_all_jobs():
    """ Loads all the jobs """
    load_healthcheck_schedule()
    load_db_backup_schedule()


def run_backup_db():
    """Back up the database """
    back_up_db()
    ping_healthchecks('backup-db')


if __name__ == "__main__":
    load_all_jobs()
    scheduler.start()
