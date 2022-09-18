import time
import schedule
import logging

from update_win_loss import update_win_loss as do_update
from send_message_to_admin import send_message

WIN_LOSS_JOB_TAG = 'win-loss-job'

MON_THU_START_TIME = "16:00"
SAT_SUN_START_TIME = "09:00"
ALL_GAMES_END_TIME = "22:00"

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
    schedule.every().thursday.at(MON_THU_START_TIME).do(start_updating_win_loss)
    schedule.every().thursday.at(ALL_GAMES_END_TIME).do(stop_updating_win_loss)

    # Monitor Saturday games (when they start)
    schedule.every().saturday.at(SAT_SUN_START_TIME).do(start_updating_win_loss)
    schedule.every().saturday.at(ALL_GAMES_END_TIME).do(stop_updating_win_loss)

    # Monitor Sunday all games throughout the day
    schedule.every().sunday.at(SAT_SUN_START_TIME).do(start_updating_win_loss)
    schedule.every().sunday.at(ALL_GAMES_END_TIME).do(stop_updating_win_loss)

    # Monitor Monday Night Football
    schedule.every().monday.at(MON_THU_START_TIME).do(start_updating_win_loss)
    schedule.every().monday.at(ALL_GAMES_END_TIME).do(stop_updating_win_loss)


def main():
    load_nfl_schedule()
    send_message("The Scheduler is up and running!")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
