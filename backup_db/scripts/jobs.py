""" Starting point, this is loaded first by the scheduler """
import os
import logging
from rocketry import Rocketry

from . import back_up_db

logging.basicConfig(level=logging.INFO)
app = Rocketry()

SCHEDULE = os.getenv('SCHEDULE')

# Do once on load
back_up_db()


@app.task(SCHEDULE)
def do_backup_db():
    """ Backs up the DB on a regular schedule """
    back_up_db()
