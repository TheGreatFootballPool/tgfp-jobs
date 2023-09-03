""" Script will check for players who have not done their picks and 'nag' @mention them """
import urllib.request
import logging
import subprocess
import os
import shutil
from datetime import datetime
from subprocess import check_output, CalledProcessError

MONGO_URI = os.getenv('MONGO_URI')
BACKUP_DIR = os.getenv('BACKUP_DIR')

logging.basicConfig(level=logging.INFO)

FILENAME = f"{BACKUP_DIR}/tgfp"
CMD = [
    "mongodump",
    f"--uri={MONGO_URI}",
    "--gzip",
    f"--archive={FILENAME}"
]

HEALTHCHECK_URL_DB_BACKUP = os.getenv('HEALTHCHECK_URL_DB_BACKUP') + 'back-up-production-db'


def back_up_db():
    """ Back up the database """
    now = datetime.now()
    hourly_file = f"{FILENAME}.hourly.{now.hour}.gz"
    daily_file = f"{FILENAME}.daily.{now.day}.gz"
    monthly_file = f"{FILENAME}.monthly.{now.month}.gz"
    yearly_file = f"{FILENAME}.yearly.{now.year}.gz"

    logging.info("About to dump mongo DB using command")
    try:
        output = check_output(CMD, stderr=subprocess.STDOUT).decode("utf-8")
    except CalledProcessError as err:
        raise RuntimeError('Could not back up Mongo DB') from err

    if 'done dumping' not in output:
        raise RuntimeError('Mongo DB not backed up')
    shutil.copyfile(FILENAME, hourly_file)
    shutil.copyfile(FILENAME, daily_file)
    shutil.copyfile(FILENAME, monthly_file)
    shutil.copyfile(FILENAME, yearly_file)
    os.remove(FILENAME)

    with urllib.request.urlopen(HEALTHCHECK_URL_DB_BACKUP, timeout=10) as response:
        logging.info(response.read())


if __name__ == '__main__':
    back_up_db()
