import os
import time
import schedule
import logging
from datetime import datetime
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from include import load_schedule

from update_win_loss import update_win_loss as do_update_win_loss
from send_message_to_admin import send_message
from create_picks import create_picks as do_create_picks
from nag_players import nag_players as do_nag_players

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


def load_tgfp_tasks():
    schedule.every().wednesday.at(PICKS_PAGE_TIME).do(create_picks)


def load_nag_tasks():
    schedule.every().thursday.at(FIRST_NAG_TIME).do(nag_players)
    schedule.every().thursday.at(SECOND_NAG_TIME).do(nag_players)
    schedule.every().thursday.at(THIRD_NAG_TIME).do(nag_players)


def main():
    load_schedule.load()
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
    logging.info("The Scheduler is up and running!")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
