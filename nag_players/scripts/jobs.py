""" Starting point, this is loaded first by the scheduler """
import logging
import os
from players_nag import nag_players
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger

logging.basicConfig(level=logging.INFO)


GAME_START_DAY_OF_WEEK = os.getenv('GAME_START_DAY_OF_WEEK')
GAME_START_TIME = os.getenv('GAME_START_TIME')
TZ = os.getenv('TZ')

scheduler = BlockingScheduler()
scheduler.configure(timezone=TZ)


h, m = GAME_START_TIME.split(':')
h: int = int(h)
m: int = int(m)
min_since_midnight = (h*60)+m

h, m = divmod(min_since_midnight-7, 60)
first_warn_trigger = CronTrigger(day_of_week=GAME_START_DAY_OF_WEEK, hour=h, minute=m)
h, m = divmod(min_since_midnight-6, 60)
second_warn_trigger = CronTrigger(day_of_week=GAME_START_DAY_OF_WEEK, hour=h, minute=m)
h, m = divmod(min_since_midnight-5, 60)
third_warn_trigger = CronTrigger(day_of_week=GAME_START_DAY_OF_WEEK, hour=h, minute=m)

all_triggers = OrTrigger([
    first_warn_trigger, second_warn_trigger, third_warn_trigger
])


def schedule_nag():
    """ Creates the picks page on the given schedule """
    nag_players()


if __name__ == "__main__":
    scheduler.add_job(schedule_nag, all_triggers)
    scheduler.start()
