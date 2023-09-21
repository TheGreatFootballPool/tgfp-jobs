cd /app/scripts
prefect --no-prompt deploy --all
prefect worker start --pool 'tgfp-jobs'