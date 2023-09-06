""" Starting point, this is loaded first by the scheduler """
import os
import logging
from rocketry import Rocketry

from picks_create import create_picks

logging.basicConfig(level=logging.INFO)
app = Rocketry()

SCHEDULE = os.getenv('SCHEDULE')


@app.task(SCHEDULE)
def create_picks_page():
    """ Creates the picks page on the given schedule """
    create_picks()
