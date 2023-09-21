""" Script will check for players who have not done their picks and 'nag' @mention them """
import os
import shutil
import subprocess
from datetime import datetime
from subprocess import check_output, CalledProcessError
from prefect import get_run_logger, flow
from prefect_helpers import helpers


@flow
def back_up_db():
    """ Back up the database """
    logger = get_run_logger()
    backup_dir = helpers.get_secret('backup_dir', is_var=True)
    username = helpers.get_secret('mongo-root-username')
    password = helpers.get_secret('mongo-root-password')
    hostname = helpers.get_secret('mongo_host', is_var=True)

    filename = f"{backup_dir}/tgfp"
    cmd = [
        "mongodump",
        "--username",
        username,
        "--password",
        password,
        "--host",
        f"{hostname}:27017",
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
