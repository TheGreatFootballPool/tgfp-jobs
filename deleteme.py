""" Delete ME """
import asyncio
from datetime import datetime, timedelta
from typing import List

import pytz
from prefect import get_client
from prefect.client.schemas import FlowRun
from prefect.client.schemas.filters import DeploymentFilter, DeploymentFilterName
from prefect.deployments import run_deployment


async def get_flow_runs():
    async with get_client() as client:
        flow_runs: List[FlowRun] = await client.read_flow_runs()
        for flow_run in flow_runs:
            if flow_run.state_name == "Running":
                print(flow_run)
        return flow_runs

if __name__ == '__main__':
    asyncio.run(get_flow_runs())

    # deploy = Deployment(
    #     name="Update Win Loss Scores",
    #     flow_name="run-update-win-loss"
    # )
    # print(deploy.is_schedule_active)
    # deploy.is_schedule_active = True
    # deploy.schedule = IntervalSchedule(interval=timedelta(minutes=5))
    # deploy.apply()
