from discord import Webhook, AsyncWebhookAdapter, Embed
import discord
import json
import aiohttp
from queue import Queue

client = discord.Client()
dbQueue = Queue()
f = open('config.json', 'r')
config = json.load(f)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    guildsList = config.get("SERVERS").keys()
    guild = message.guild.name
    channel = message.channel.name
    if guild in guildsList:
        channels = config.get("SERVERS").get(guild)
        if channel in channels:
            for word in config.get("KEYWORDS"):
                if word.lower() in message.content.lower():
                    await sendToTarget(message)


async def sendToTarget(message):
    embed = Embed(title='Keyword Detected!')
    embed.add_field(name='Server Name', value=message.guild.name, inline=False)
    embed.add_field(name='Channel Name',
                    value=message.channel.name, inline=False)
    embed.add_field(name='User', value=message.author.name, inline=False)
    embed.description = message.content
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(
            config.get("OUTPUT_CHANNEL_WEBHOOK"), adapter=AsyncWebhookAdapter(session))
        await webhook.send(embed=embed, username='Discord Monitor')

client.run(config.get("USER_TOKEN"), bot=False)
