""" Starting point, this is loaded first by the scheduler """
import logging
import os
from win_loss_update import update_win_loss
from apscheduler.schedulers.blocking import BlockingScheduler

TZ = os.getenv('TZ')

logging.basicConfig(level=logging.INFO)

scheduler = BlockingScheduler()
scheduler.configure(timezone=TZ)


def do_win_loss():
    """ Creates the picks page on the given schedule """
    update_win_loss()


if __name__ == "__main__":
    scheduler.add_job(do_win_loss, 'interval', minutes=5)
    scheduler.start()
