from datetime import timedelta, datetime
from time import sleep

from prefect import flow
from prefect.client.schemas.schedules import IntervalSchedule
from prefect.deployments import run_deployment
from prefect.logging import get_logger


@flow
def slow_run(name: str):
    """ Runs slowly """
    sleep(120)
    logger = get_logger()
    logger.info(f"finally done with {name}")


if __name__ == '__main__':
    run_date: datetime = datetime.utcnow() + timedelta(minutes=5)
    run_date2: datetime = run_date + timedelta(minutes=20)
    run_deployment(name="7e370338-a3b5-4cf6-944a-3708f53a82b7", scheduled_time=run_date, timeout=0)
    run_deployment(name="7e370338-a3b5-4cf6-944a-3708f53a82b7", scheduled_time=run_date2, timeout=0)
    # deployment = backup_db_deploy = slow_run.to_deployment(
    #     schedule=IntervalSchedule(interval=timedelta(minutes=1)),
    #     name="Slow Run",
    #     description="Runs, slowly",
    #     version="0.1"
    # )
