from prefect.deployments import Deployment

if __name__ == '__main__':
    deploy = Deployment(
        name="Update Win / Loss / Scores",
        flow_name="run-update-win-loss"
    )
    print(deploy.is_schedule_active)
    deploy.is_schedule_active = False
    deploy.apply()
