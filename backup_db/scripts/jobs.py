""" Starting point, this is loaded first by the scheduler """
import os
import logging
from db_backup import back_up_db

logging.basicConfig(level=logging.INFO)

SCHEDULE = os.getenv('SCHEDULE')
logging.info(SCHEDULE)


def do_backup_db():
    """ Backs up the DB on a regular schedule """
    back_up_db()

if __name__ == "__main__":
    app.run()
