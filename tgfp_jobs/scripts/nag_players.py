""" Script will check for players who have not done their picks and 'nag' @mention them """
# pylint: disable=F0401
import discord
import paho.mqtt.client as mqtt
from prefect import flow
from prefect.logging import get_logger

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
# pylint: disable=F0401
from config import get_config, Config
config: Config = get_config()


@flow
def nag_the_players():
    """ Nag the players that didn't do their picks """
    logger = get_logger()
    logger.info("Ready to nag the player")
    mqtt_client = mqtt.Client()
    mqtt_client.connect(config.MQTT_HOST)
    logger.info("About to send the message")
    mqtt_client.publish("tgfp-bot/nag-bot", payload="DevNag")
    logger.info("Sent message to mqtt")


if __name__ == '__main__':
    nag_the_players()
