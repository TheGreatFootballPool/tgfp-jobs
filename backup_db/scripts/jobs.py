""" Starting point, this is loaded first by the scheduler """
import os
import logging
from rocketry import Rocketry
from db_backup import back_up_db

logging.basicConfig(level=logging.INFO)
app = Rocketry()

SCHEDULE = os.getenv('SCHEDULE')
logging.info(SCHEDULE)


@app.task(SCHEDULE)
def do_backup_db():
    """ Backs up the DB on a regular schedule """
    back_up_db()

if __name__ == "__main__":
    app.run()
