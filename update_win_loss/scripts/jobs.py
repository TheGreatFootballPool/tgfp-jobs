""" Starting point, this is loaded first by the scheduler """
import logging
import os
from datetime import datetime, timedelta
from typing import List
import pytz
from tgfp_lib import TGFPGame
from win_loss_update import this_weeks_games
from win_loss_update import update_win_loss
from apscheduler.schedulers.blocking import BlockingScheduler

TZ = os.getenv('TZ')
CREATE_PICKS_DAY_OF_WEEK = os.getenv('CREATE_PICKS_DAY_OF_WEEK')
# We want to schedule the update win loss after we've created the picks page
CREATE_SCHEDULE_HOUR = int(os.getenv('CREATE_PICKS_HOUR')) + 1

logging.basicConfig(level=logging.INFO)

scheduler = BlockingScheduler()
scheduler.configure(timezone=TZ)


def do_win_loss(tgfp_game: TGFPGame):
    """ Creates the picks page on the given schedule """
    update_win_loss(tgfp_game)


# Basic concept, every day at 1am, run a 'scheduler' by getting the start time of the games
#   for today, then

# This job runs every day at 1am
def weekly_job_sweep():
    """ Every week go get the games, and add the jobs to the scheduler for each game """
    games: List[TGFPGame] = this_weeks_games()
    for game in games:
        start_date: datetime = game.pacific_start_time
        end_date: datetime = start_date + timedelta(hours=5)
        log_msg: str = f"Adding game monitor: {game.tgfp_nfl_game_id} for time {start_date}"
        logging.info(log_msg)
        scheduler.add_job(
            do_win_loss,
            'interval',
            minutes=5,
            timezone=pytz.timezone(TZ),
            start_date=start_date,
            end_date=end_date,
            args=[game]
        )

if __name__ == "__main__":
    # run weekly_job_sweep once (startup)
    weekly_job_sweep()
    # Add job for weekly job sweep
    scheduler.add_job(
        weekly_job_sweep,
        'cron',
        day_of_week=CREATE_PICKS_DAY_OF_WEEK,
        hour=CREATE_SCHEDULE_HOUR
    )
    scheduler.start()
