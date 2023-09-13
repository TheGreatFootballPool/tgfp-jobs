""" This will use mqtt to publish tasks to the job scheduler to run as 1-off """
import argparse
import logging
import os

from paho.mqtt import publish

LOG_LEVEL: str = os.getenv('LOG_LEVEL')
logging.basicConfig(level=LOG_LEVEL)
MQTT_HOST: str = os.getenv('MQTT_HOST')
parser = argparse.ArgumentParser(
                    prog='TGFP Task Runner',
                    description='What the program does',
                    epilog='Text at the bottom of help')
parser.add_argument('--create_picks', action='store_true')
parser.add_argument('--create_win_loss_schedule', action='store_true')
parser.add_argument('--create_nag_player_schedule', action='store_true')


def main():
    """ Publishes the topic based on input"""
    args = parser.parse_args()
    if args.create_picks:
        publish.single('tgfp/create_picks', hostname=MQTT_HOST)
    if args.create_win_loss_schedule:
        publish.single('tgfp/create_win_loss_schedule', hostname=MQTT_HOST)
    if args.create_nag_player_schedule:
        publish.single('tgfp/create_nag_player_schedule', hostname=MQTT_HOST)


if __name__ == '__main__':
    main()
