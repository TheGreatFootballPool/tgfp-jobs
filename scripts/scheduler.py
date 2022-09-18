import time
import schedule
import logging
from datetime import datetime

from update_win_loss import update_win_loss as do_update
from send_message_to_admin import send_message

WIN_LOSS_JOB_TAG = 'win-loss-job'

START_TIME = "09:00"
END_TIME = "22:00"

logger = logging.getLogger('mylogger')

logging.basicConfig(
    filename='/var/log/scheduler.log',
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)


def start_updating_win_loss():
    send_message("🏁Starting to monitor win/loss and scores")
    schedule.every(5).seconds.do(update_win_loss).tag(WIN_LOSS_JOB_TAG)


def stop_updating_win_loss():
    send_message("🛑Stopping monitoring win/loss and scores")
    schedule.clear(WIN_LOSS_JOB_TAG)


def update_win_loss():
    logging.info("Running 'update_win_loss'")
    do_update()


def load_nfl_schedule():
    """ This is the schedule of when NFL games run """

    # Monitor Thursday night games
    schedule.every().thursday.at(START_TIME).do(start_updating_win_loss)
    schedule.every().thursday.at(END_TIME).do(stop_updating_win_loss)

    # Monitor Saturday games (when they start)
    schedule.every().saturday.at(START_TIME).do(start_updating_win_loss)
    schedule.every().saturday.at(END_TIME).do(stop_updating_win_loss)

    # Monitor Sunday all games throughout the day
    schedule.every().sunday.at(START_TIME).do(start_updating_win_loss)
    schedule.every().sunday.at(END_TIME).do(stop_updating_win_loss)

    # Monitor Monday Night Football
    schedule.every().monday.at(START_TIME).do(start_updating_win_loss)
    schedule.every().monday.at(END_TIME).do(stop_updating_win_loss)


def main():
    load_nfl_schedule()
    # start the schedule if we're starting up during a window
    # 0 == Monday
    # 3 == Thursday
    # 4 == Saturday
    # 5 == Sunday
    dt = datetime.now()
    day = dt.weekday()
    hour = dt.hour
    if day in [0, 3, 4, 5]:
        if 8 < hour < 22:
            start_updating_win_loss()
    send_message("The Scheduler is up and running!")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
