""" Starting point, this is loaded first by the scheduler """
import logging
import os
import schedule
import sentry_sdk
from datetime import datetime

from . import create_picks
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN_TGFP_BIN'),
    traces_sample_rate=1.0
)
logging.basicConfig(level=logging.INFO)

PICKS_PAGE_TIME = "06:00"


def load():
    logging.info("loading Create Picks schedule")
    schedule.every().wednesday.at(PICKS_PAGE_TIME).do(create_picks)
