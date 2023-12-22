""" Configuration file """
import os
import pathlib

from .prefect_helpers import PrefectHelper


# pylint: disable=too-few-public-methods
class Config:
    """ Base configuration class """
    ENVIRONMENT: str = os.getenv('ENVIRONMENT')
    assert ENVIRONMENT is not None
    helper = PrefectHelper(ENVIRONMENT)
    BASE_DIR = pathlib.Path(__file__).parent.parent
    COGS_DIR = BASE_DIR / "cogs"
    CMD_DIR = BASE_DIR / "cmds"
    MONGO_ROOT_USERNAME: str = helper.get_secret('mongo-root-username')
    MONGO_ROOT_PASSWORD: str = helper.get_secret('mongo-root-password')
    MONGO_HOST: str = helper.get_variable('mongo_host')
    MONGO_URI: str = (f"mongodb://{MONGO_ROOT_USERNAME}:"
                      f"{MONGO_ROOT_PASSWORD}@{MONGO_HOST}:27017/"
                      f"?authMechanism=DEFAULT&authSource=admin")
    OAUTHLIB_INSECURE_TRANSPORT: str = helper.get_variable('discord_oauthlib_insecure_transport')
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = OAUTHLIB_INSECURE_TRANSPORT
    DISCORD_CLIENT_ID: str = helper.get_secret('discord-client-id')
    DISCORD_CLIENT_SECRET: str = helper.get_secret('discord-client-secret')
    DISCORD_REDIRECT_URI: str = helper.get_variable('discord_redirect_uri')
    DISCORD_AUTH_TOKEN: str = helper.get_secret('discord-auth-token')
    DISCORD_GUILD_NAME: str = helper.get_variable('discord_guild_name')
    DISCORD_GUILD_ID: int = int(helper.get_variable('discord_guild_id'))
    DISCORD_NAG_BOT_CHANNEL_ID: int = int(helper.get_variable('discord_nag_bot_channel_id'))
    DISCORD_BOT_CHAT_CHANNEL_ID: int = int(helper.get_variable('discord_bot_chat_channel_id'))
    BACKUP_DIR: str = helper.get_variable('backup_dir')
    SECRET_KEY: str = helper.get_secret('web-secret-key')
    LISTMONK_AUTH_HASH: str = helper.get_variable('listmonk_auth_hash')
    LISTMONK_LIST_ID: int = int(helper.get_variable('listmonk_list_id'))
    LISTMONK_API_URL: str = helper.get_variable('listmonk_api_url')
    MQTT_HOST: str = helper.get_variable('mqtt_host')


def get_config():
    """ Factory method for returning the correct config"""
    return Config()
