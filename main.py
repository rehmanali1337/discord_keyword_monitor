from discord import Webhook, AsyncWebhookAdapter, Embed
import discord
import json
import aiohttp
from queue import Queue
import threading
import re
from exts.db import DB

client = discord.Client()
dbQueue = Queue()
f = open('config.json', 'r')
config = json.load(f)
set1 = config.get("SET1")
set2 = config.get("SET2")
set3 = config.get("SET3")


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


async def valid(text):
    set1Found = False
    set2Found = False
    set3Found = False
    for w in set1:
        if w.lower() in text.lower():
            set1Found = True
            print('Set 1 passed!')
    for w in set2:
        if w.lower() in text.lower():
            set2Found = True
            print('Set 2 passed!')
    for w in set3:
        if w.lower() in text.lower():
            set3Found = True
            print('Set 3 passed!')
    if '$' in text:
        set3Found = True
        print('$ passed!')

    def createWords(text):
        sublists = [s for s in text.split('\n')]
        words = []
        for l in sublists:
            finalList = l.split(' ')
            words.extend([w for w in finalList])
        words = list(filter(None, words))
        string = ' '.join(words)
        words = ''.join(
            ch for ch in string if ch.isalnum() or ch == ' ')
        return [w for w in words.split(' ')]

    words = createWords(text)
    for w in words:
        if len(w) <= 4 and len(w) >= 1:
            if w.isupper():
                set3Found = True
    if set1Found and set2Found and set3Found:
        print('All tests passed!')
        return True
    return False


def deEmojify(text):
    regrex_pattern = re.compile(pattern="["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


@client.event
async def on_message(message):
    guildsList = list(config.get("SERVERS").keys())
    guild = deEmojify(message.guild.name.strip())
    guild = guild.strip()
    channel = deEmojify(message.channel.name.strip())
    channel = channel.strip()
    print(f'{guild} --> {channel}')
    if guild in guildsList:
        print('Valid Server')
        channels = config.get("SERVERS").get(guild)
        if channel in channels:
            print('Valid channel')
            if await valid(message.content):
                print('Sending to target!')
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

# db = DB(dbQueue)
# threading.Thread(target=db.start).start()

client.run(config.get("USER_TOKEN"), bot=False)
