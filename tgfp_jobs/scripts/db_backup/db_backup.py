""" Script will check for players who have not done their picks and 'nag' @mention them """
import subprocess
import os
import shutil
from datetime import datetime
from subprocess import check_output, CalledProcessError

from prefect import get_run_logger

MONGO_URI = os.getenv('MONGO_URI')
BACKUP_DIR = os.getenv('BACKUP_DIR')
MONGO_INITDB_ROOT_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_INITDB_ROOT_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_PORT = os.getenv('MONGO_PORT')

FILENAME = f"{BACKUP_DIR}/tgfp"
CMD = [
    "mongodump",
    "--username",
    MONGO_INITDB_ROOT_USERNAME,
    "--password",
    MONGO_INITDB_ROOT_PASSWORD,
    "--host",
    f"{MONGO_HOST}:{MONGO_PORT}",
    "--gzip",
    f"--archive={FILENAME}"
]


def back_up_db():
    """ Back up the database """
    logger = get_run_logger()

    now = datetime.now()
    hourly_file = f"{FILENAME}.hourly.{now.hour}.gz"
    daily_file = f"{FILENAME}.daily.{now.day}.gz"
    monthly_file = f"{FILENAME}.monthly.{now.month}.gz"
    yearly_file = f"{FILENAME}.yearly.{now.year}.gz"

    logger.info("About to dump mongo DB using command")
    try:
        output = check_output(CMD, stderr=subprocess.STDOUT).decode("utf-8")
    except CalledProcessError as err:
        errmsg: str = f'Could not back up Mongo DB: {str(err)}'
        logger.error(errmsg)
        raise RuntimeError(errmsg) from err
    if 'done dumping' not in output:
        errmsg: str = f'Mongo DB not backed up: {output}'
        logger.error(errmsg)
        raise RuntimeError(errmsg)
    shutil.copyfile(FILENAME, hourly_file)
    shutil.copyfile(FILENAME, daily_file)
    shutil.copyfile(FILENAME, monthly_file)
    shutil.copyfile(FILENAME, yearly_file)
    os.remove(FILENAME)


if __name__ == '__main__':
    back_up_db()
