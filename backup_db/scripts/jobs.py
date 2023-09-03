""" Starting point, this is loaded first by the scheduler """
import logging
import schedule
from . import back_up_db

logging.basicConfig(level=logging.INFO)


def load():
    """ Load the schedule """
    logging.info("Loading the db backup schedule")
    back_up_db()  # Do once on startup
    schedule.every(30).minutes.do(back_up_db)
