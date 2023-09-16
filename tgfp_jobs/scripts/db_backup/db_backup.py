""" Script will check for players who have not done their picks and 'nag' @mention them """
import subprocess
import os
import shutil
from datetime import datetime
from subprocess import check_output, CalledProcessError
from prefect.blocks.system import Secret
from prefect import get_run_logger, variables

ENV: str = os.getenv('ENVIRONMENT')


def get_secret(secret_name: str, is_var: bool = False, use_env: bool = True) -> str:
    """ Retrieves the secret or variable, using the current environment """
    secret_string: str
    env_string: str = ENV if use_env else ""
    if is_var:
        return str(variables.get(f"{secret_name}_{env_string}"))
    with Secret.load(f"{secret_name}-{env_string}") as a_secret:
        secret_string = a_secret.get()
    return secret_string


MONGO_URI = get_secret('mongo-uri')
BACKUP_DIR = get_secret('backup_dir', is_var=True)
MONGO_INITDB_ROOT_USERNAME = get_secret('mongo-root-username')
MONGO_INITDB_ROOT_PASSWORD = get_secret('mongo-root-password')
MONGO_HOST = get_secret('mongo_host', is_var=True)
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
