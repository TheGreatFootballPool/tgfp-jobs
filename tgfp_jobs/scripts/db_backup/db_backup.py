""" Script will check for players who have not done their picks and 'nag' @mention them """
import os
import shutil
import subprocess
from datetime import datetime
from subprocess import check_output, CalledProcessError
from prefect import get_run_logger
from scripts.prefect_helpers import helpers

ENV: str = os.getenv('ENVIRONMENT')


MONGO_URI = helpers.get_secret('mongo-uri')
BACKUP_DIR = helpers.get_secret('backup_dir', is_var=True)
MONGO_INITDB_ROOT_USERNAME = helpers.get_secret('mongo-root-username')
MONGO_INITDB_ROOT_PASSWORD = helpers.get_secret('mongo-root-password')
MONGO_HOST = helpers.get_secret('mongo_host', is_var=True)
MONGO_PORT = 27017

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
