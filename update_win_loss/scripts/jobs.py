""" Starting point, this is loaded first by the scheduler """
import logging
import os
import schedule
import sentry_sdk
from datetime import datetime

from . import update_win_loss
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN_TGFP_BIN'),
    traces_sample_rate=1.0
)
logging.basicConfig(level=logging.INFO)

WIN_LOSS_JOB_TAG = 'win-loss-job'

SUNDAY_START_TIME = "06:00"
START_TIME = "09:00"
END_TIME = "22:00"
PICKS_PAGE_TIME = "06:00"
FIRST_NAG_TIME = "16:00"
SECOND_NAG_TIME = "16:50"
THIRD_NAG_TIME = "17:10"


def start_updating_win_loss():
    logging.info("🏁Starting to monitor win/loss and scores")
    schedule.every(5).minutes.do(do_update_win_loss).tag(WIN_LOSS_JOB_TAG)


def stop_updating_win_loss():
    logging.info("🛑Stopping monitoring win/loss and scores")
    schedule.clear(WIN_LOSS_JOB_TAG)


def do_update_win_loss():
    logging.info("Running 'update_win_loss'")
    update_win_loss()


def load():
    # Monitor Thursday night games
    schedule.every().thursday.at(START_TIME).do(start_updating_win_loss)
    schedule.every().thursday.at(END_TIME).do(stop_updating_win_loss)

    # Monitor Saturday games (when they start)
    schedule.every().saturday.at(START_TIME).do(start_updating_win_loss)
    schedule.every().saturday.at(END_TIME).do(stop_updating_win_loss)

    # Monitor Sunday all games throughout the day
    schedule.every().sunday.at(SUNDAY_START_TIME).do(start_updating_win_loss)
    schedule.every().sunday.at(END_TIME).do(stop_updating_win_loss)

    # Monitor Monday Night Football
    schedule.every().monday.at(START_TIME).do(start_updating_win_loss)
    schedule.every().monday.at(END_TIME).do(stop_updating_win_loss)
    dt = datetime.now()
    day = dt.weekday()
    hour = dt.hour
    if day in [0, 3, 5, 6]:
        if 8 < hour < 22:
            start_updating_win_loss()

