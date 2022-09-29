import os
import time
import schedule
import logging
from datetime import datetime
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from update_win_loss import update_win_loss as do_update_win_loss
from send_message_to_admin import send_message
from create_picks import create_picks as do_create_picks
from nag_players import nag_players as do_nag_players

sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN_TGFP_BIN'),
    integrations=[
        sentry_logging,
    ],
    traces_sample_rate=1.0
)

WIN_LOSS_JOB_TAG = 'win-loss-job'

SUNDAY_START_TIME = "06:00"
START_TIME = "09:00"
END_TIME = "22:00"
PICKS_PAGE_TIME = "06:00"
FIRST_NAG_TIME = "16:00"
SECOND_NAG_TIME = "16:50"
THIRD_NAG_TIME = "17:10"


def start_updating_win_loss():
    send_message("🏁Starting to monitor win/loss and scores")
    schedule.every(5).seconds.do(update_win_loss).tag(WIN_LOSS_JOB_TAG)


def stop_updating_win_loss():
    send_message("🛑Stopping monitoring win/loss and scores")
    schedule.clear(WIN_LOSS_JOB_TAG)


def update_win_loss():
    logging.info("Running 'update_win_loss'")
    do_update_win_loss()


def create_picks():
    logging.info("It's wednesday morning!  About to create the picks page")
    do_create_picks()


def nag_players():
    logging.info("Nag bot running!")
    do_nag_players()


def load_nfl_schedule():
    """ This is the schedule of when NFL games run """

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


def load_tgfp_tasks():
    schedule.every().wednesday.at(PICKS_PAGE_TIME).do(create_picks)


def load_nag_tasks():
    schedule.every().thursday.at(FIRST_NAG_TIME).do(nag_players)
    schedule.every().thursday.at(SECOND_NAG_TIME).do(nag_players)
    schedule.every().thursday.at(THIRD_NAG_TIME).do(nag_players)


def main():
    logging.info("about to load the schedule")
    load_nfl_schedule()
    logging.info("about to load the other misc. tgfp_tasks")
    load_tgfp_tasks()
    logging.info("about to load nag tasks")
    load_nag_tasks()
    # start the schedule if we're starting up during a window
    # 0 == Monday
    # 3 == Thursday
    # 4 == Saturday
    # 5 == Sunday
    dt = datetime.now()
    day = dt.weekday()
    hour = dt.hour
    if day in [0, 3, 5, 6]:
        if 8 < hour < 22:
            start_updating_win_loss()
    send_message("The Scheduler is up and running!")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
