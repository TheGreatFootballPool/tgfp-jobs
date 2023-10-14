""" Configuration file """
import os

from .prefect_helpers import PrefectHelper


# pylint: disable=too-few-public-methods
class Config:
    """ Base configuration class """
    ENVIRONMENT: str = os.getenv('ENVIRONMENT')
    assert ENVIRONMENT is not None
    helper = PrefectHelper(ENVIRONMENT)

    MONGO_URI: str = helper.get_secret('mongo-uri')
    MONGO_ROOT_USERNAME: str = helper.get_secret('mongo-root-username')
    MONGO_ROOT_PASSWORD: str = helper.get_secret('mongo-root-password')
    MONGO_HOST: str = helper.get_variable('mongo_host')
    OAUTHLIB_INSECURE_TRANSPORT: str = helper.get_variable('discord_oauthlib_insecure_transport')
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = OAUTHLIB_INSECURE_TRANSPORT
    DISCORD_CLIENT_ID: str = helper.get_secret('discord-client-id')
    DISCORD_CLIENT_SECRET: str = helper.get_secret('discord-client-secret')
    DISCORD_REDIRECT_URI: str = helper.get_variable('discord_redirect_uri')
    DISCORD_AUTH_TOKEN: str = helper.get_secret('discord-auth-token')
    DISCORD_GUILD_NAME: str = helper.get_variable('discord_guild_name')
    BACKUP_DIR = helper.get_variable('backup_dir')
    SECRET_KEY = helper.get_secret('web-secret-key')
    LISTMONK_AUTH_HASH = helper.get_variable('listmonk_auth_hash')
    LISTMONK_LIST_ID = helper.get_variable('listmonk_list_id')
    LISTMONK_API_URL = helper.get_variable('listmonk_api_url')


def get_config():
    """ Factory method for returning the correct config"""
    return Config()
