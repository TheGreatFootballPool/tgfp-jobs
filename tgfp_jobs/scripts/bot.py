"""This example requires the 'message_content' intent."""
import asyncio
from contextlib import AsyncExitStack

# pylint: disable=F0401
import aiomqtt
import discord

from config import get_config


config = get_config()

NAG_CHANNEL = config.DISCORD_NAG_BOT_CHANNEL_ID


class Bot(discord.Client):
    """ TGFP Bot """
    def __init__(self, *, mqtt_client, intents, **options) -> None:
        super().__init__(intents=intents, **options)
        self.mqtt_client: aiomqtt.Client = mqtt_client

    @staticmethod
    async def on_ready():
        """ On Ready """
        print("I am ready!")

    async def setup_hook(self) -> None:
        """ Setup hook """
        asyncio.create_task(self.subscriber())

    async def subscriber(self):
        """ Subscriber """
        await self.wait_until_ready()
        # noinspection PyTypeChecker
        await self.mqtt_client.subscribe("tgfp-bot/#")

        print("Started listening to messages from MQTT...")
        async with self.mqtt_client.messages() as messages:
            message: aiomqtt.client.Message
            async for message in messages:
                if message.topic.matches("tgfp-bot/nag-bot"):
                    channel: discord.TextChannel = self.get_channel(NAG_CHANNEL)
                    await channel.send(f"Content from MQTT: {message.payload}")

    async def on_message(self, message: discord.Message):
        """ On Message """
        if message.author.bot:
            return

        asyncio.create_task(
            message.reply(f'User {message.author.mention} said: "{message.clean_content}"')
        )
        # noinspection PyTypeChecker
        asyncio.create_task(
            self.mqtt_client.publish("tgfp-bot/nag-bot", payload=message.content)
        )


async def main():
    """ Main method """
    token = config.DISCORD_AUTH_TOKEN

    async with AsyncExitStack() as astack:
        mqtt_client = await astack.enter_async_context(aiomqtt.Client("goshdarnedserver.lan"))

        intents = discord.Intents.default()
        intents.message_content = True
        bot = await astack.enter_async_context(Bot(mqtt_client=mqtt_client, intents=intents))

        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
