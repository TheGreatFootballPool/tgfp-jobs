""" Starting point, this is loaded first by the scheduler """
import os
import logging
from db_backup import back_up_db
from apscheduler.schedulers.blocking import BlockingScheduler

TZ = os.getenv('TZ')
DB_BACKUP_INTERVAL_MINUTES = os.getenv('DB_BACKUP_INTERVAL_MINUTES')

logging.basicConfig(level=logging.INFO)

scheduler = BlockingScheduler()
scheduler.configure(timezone=TZ)


def do_backup_db():
    """ Backs up the DB on a regular schedule """
    back_up_db()

if __name__ == "__main__":
    scheduler.add_job(do_backup_db, 'interval', minutes=DB_BACKUP_INTERVAL_MINUTES)
    scheduler.start()
