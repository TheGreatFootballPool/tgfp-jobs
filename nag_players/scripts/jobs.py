""" Starting point, this is loaded first by the scheduler """
import logging
import os
import schedule
import sentry_sdk
from . import nag_players

FIRST_NAG_TIME = "16:00"
SECOND_NAG_TIME = "16:50"
THIRD_NAG_TIME = "17:10"

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN_TGFP_BIN'),
    traces_sample_rate=1.0
)
logging.basicConfig(level=logging.INFO)


def load():
    logging.info("loading Nag Players schedule")
    schedule.every().thursday.at(FIRST_NAG_TIME).do(nag_players)
    schedule.every().thursday.at(SECOND_NAG_TIME).do(nag_players)
    schedule.every().thursday.at(THIRD_NAG_TIME).do(nag_players)
