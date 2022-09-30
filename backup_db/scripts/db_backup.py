""" Script will check for players who have not done their picks and 'nag' @mention them """
import urllib.request
import logging
import subprocess
import os
import shutil
from datetime import datetime
from subprocess import check_output, CalledProcessError

MONGO_BACKUP_URI = os.getenv('MONGO_BACKUP_URI')
BACKUP_DIR = os.getenv('BACKUP_DIR')

logging.basicConfig(level=logging.INFO)
dt = datetime.now()
month = dt.month

FILENAME = f"{BACKUP_DIR}/tgfp"
HOURLY_FILE = f"{FILENAME}.hourly.{dt.hour}.gz"
DAILY_FILE = f"{FILENAME}.daily.{dt.day}.gz"
MONTHLY_FILE = f"{FILENAME}.monthly.{dt.month}.gz"
YEARLY_FILE = f"{FILENAME}.yearly.{dt.year}.gz"

CMD = [
    "mongodump",
    f"--uri={MONGO_BACKUP_URI}",
    "--gzip",
    f"--archive={FILENAME}"
]


def db_backup():
    logging.info("About to dump mongo DB using command")
    try:
        output = check_output(CMD, stderr=subprocess.STDOUT).decode("utf-8")
    except CalledProcessError as err:
        raise RuntimeError('Could not back up Mongo DB') from err

    if 'done dumping' not in output:
        raise RuntimeError('Mongo DB not backed up')
    shutil.copyfile(FILENAME, HOURLY_FILE)
    shutil.copyfile(FILENAME, DAILY_FILE)
    shutil.copyfile(FILENAME, MONTHLY_FILE)
    shutil.copyfile(FILENAME, YEARLY_FILE)
    os.remove(FILENAME)
    urllib.request.urlopen(
        "https://hc-ping.com/4b181d15-e36d-44f4-b7d4-498ab03f71c7",
        timeout=10
    )


if __name__ == '__main__':
    db_backup()
