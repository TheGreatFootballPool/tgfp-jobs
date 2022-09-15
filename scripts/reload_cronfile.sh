#!/bin/bash
if [ -f /data/my-crontab ]; then
  cp /data/my-crontab /etc/cron.d/my-crontab
  chmod 0644 /etc/cron.d/my-crontab
  crontab /etc/cron.d/my-crontab
else
  echo "No crontab file found, please add my-crontab to the /data directory"
fi
