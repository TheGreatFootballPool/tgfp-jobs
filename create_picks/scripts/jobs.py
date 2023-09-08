""" Starting point, this is loaded first by the scheduler """
import os
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from picks_create import create_picks

CREATE_PICKS_DAY_OF_WEEK = os.getenv('CREATE_PICKS_DAY_OF_WEEK')
CREATE_PICKS_HOUR = int(os.getenv('CREATE_PICKS_HOUR'))
TZ = os.getenv('TZ')

logging.basicConfig(level=logging.INFO)
scheduler = BlockingScheduler()
scheduler.configure(timezone=TZ)


def create_picks_page():
    """ Creates the picks page on the given schedule """
    create_picks()

if __name__ == "__main__":
    scheduler.add_job(
        create_picks_page,
        'cron',
        day_of_week=CREATE_PICKS_DAY_OF_WEEK,
        hour=CREATE_PICKS_HOUR)
    scheduler.start()
