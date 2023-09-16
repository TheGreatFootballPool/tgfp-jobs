from datetime import timedelta

from prefect.client.schemas.schedules import IntervalSchedule
from prefect.deployments import Deployment

if __name__ == '__main__':
    deploy = Deployment(
        name="Update Win Loss Scores",
        flow_name="run-update-win-loss"
    )
    print(deploy.is_schedule_active)
    deploy.is_schedule_active = True
    deploy.schedule = IntervalSchedule(interval=timedelta(minutes=5))
    deploy.apply()
