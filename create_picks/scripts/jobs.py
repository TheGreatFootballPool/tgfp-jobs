""" Starting point, this is loaded first by the scheduler """
import os
import logging
import schedule

from . import create_picks

logging.basicConfig(level=logging.INFO)

CREATE_PICKS_PAGE_TIME = os.getenv('CREATE_PICKS_PAGE_TIME')


def load():
    """ Load the schedule """
    logging.info("loading Create Picks schedule")
    schedule.every().wednesday.at(CREATE_PICKS_PAGE_TIME).do(create_picks)
