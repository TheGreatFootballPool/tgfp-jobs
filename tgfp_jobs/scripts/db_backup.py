""" Script will check for players who have not done their picks and 'nag' @mention them """
import os
import shutil
import subprocess
from datetime import datetime
from subprocess import check_output, CalledProcessError
from prefect import get_run_logger, flow

from config import get_config


@flow
def back_up_db():
    """ Back up the database """
    logger = get_run_logger()
    config = get_config()

    filename = f"{config.BACKUP_DIR}/tgfp"
    cmd = [
        "mongodump",
        "--username",
        config.MONGO_ROOT_USERNAME,
        "--password",
        config.MONGO_ROOT_PASSWORD,
        "--host",
        f"{config.MONGO_HOST}:27017",
        "--gzip",
        f"--archive={filename}"
    ]

    now = datetime.now()
    hourly_file = f"{filename}.hourly.{now.hour}.gz"
    daily_file = f"{filename}.daily.{now.day}.gz"
    monthly_file = f"{filename}.monthly.{now.month}.gz"
    yearly_file = f"{filename}.yearly.{now.year}.gz"

    logger.info("About to dump mongo DB using command")
    try:
        output = check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
    except CalledProcessError as err:
        errmsg: str = f'Could not back up Mongo DB: {str(err)}'
        logger.error(errmsg)
        raise RuntimeError(errmsg) from err
    if 'done dumping' not in output:
        errmsg: str = f'Mongo DB not backed up: {output}'
        logger.error(errmsg)
        raise RuntimeError(errmsg)
    shutil.copyfile(filename, hourly_file)
    shutil.copyfile(filename, daily_file)
    shutil.copyfile(filename, monthly_file)
    shutil.copyfile(filename, yearly_file)
    os.remove(filename)
