import discord
import logging
import json
import os
from datetime import datetime, timedelta
import pytz

from boosts.winamax.script import winamax
from boosts.unibet.script import unibet
from boosts.pselZebet.script import pselZebet
from boosts.pmu.script import pmu
from boosts.netbet.script import netbet
from boosts.betclic.script import betclic

from twitter import tweet

cache_path = 'boosts'

roles = {
    'betclic': 1271667918983397438,
    'winamax': 1271668054639640627,
    'unibet': 1271668192711938069,
    'pselZebet': 1271668295287836763,
    'pmu': 1271668297066221598,
    'netbet': 1271668302464417873,
    'winamax-autres': 1272647443799998544,
    'unibet-autres': 1271668193378697277,
    'pselZebet-autres': 1271668295967309916,
    'pmu-autres': 1271668297632317541,
}

async def search_boosts(bot):
    await winamax(bot)
    await unibet(bot)
    await pselZebet(bot)
    await pmu(bot)
    await netbet(bot)
    await betclic(bot)

async def publish_boosts(bookmaker, bot, finalBoosts, color):
    MAIN_CHANNEL_ID = int(os.getenv(f'{bookmaker.upper()}_MAIN_CHANNEL_ID'))
    SECONDARY_CHANNEL_ID = int(os.getenv(f'{bookmaker.upper()}_SECONDARY_CHANNEL_ID'))
    FORUM_BOOSTS_CHANNEL_ID = int(os.getenv(f'FORUM_BOOSTS_CHANNEL_ID'))
    MT_ALL_BOOSTS_CHANNEL_ID = int(os.getenv(f'MT_ALL_BOOSTS_CHANNEL_ID'))

    mtChannel = bot.get_channel(MT_ALL_BOOSTS_CHANNEL_ID)
    boostsForum = bot.get_channel(FORUM_BOOSTS_CHANNEL_ID)
    
    cache_file_path = os.path.join(os.getcwd(), cache_path, bookmaker, 'cache.json')

    utc_time = datetime.now(pytz.utc)
    french_time = utc_time.astimezone(pytz.timezone('Europe/Paris'))
    formatted_time = french_time.strftime('%d/%m/%Y %H:%M:%S')
    
    try:
        with open(cache_file_path, 'r') as file:
            cache = json.load(file)

    except FileNotFoundError:
        cache = []

    except Exception as e:
        print(f"Error reading cache file: {e}")
        cache = []

    toDelete = [boost for boost in cache if datetime.fromisoformat(boost['startTime']).replace(tzinfo=pytz.utc) <= utc_time - timedelta(hours=5)]

    for boost in toDelete:
        thread = boostsForum.get_thread(boost['mt_forum_thread_id'])
        await thread.edit(archived=True)

    cache = [boost for boost in cache if boost not in toDelete]

    for boost in finalBoosts:
        channelId = MAIN_CHANNEL_ID if boost['bigBoost'] else SECONDARY_CHANNEL_ID   
        channel = bot.get_channel(channelId)         
        arobase = bookmaker

        if boost['bigBoost'] == False and bookmaker != 'netbet':
            arobase = f'{bookmaker}-autres'

        embed = discord.Embed(
            title=boost['title'],
            description=boost['intitule'],
            color=int(color, 16)
        )

        embed.add_field(name='Côte initiale', value=boost['odd'], inline=True)
        embed.add_field(name='Côte boostée', value=boost['boostedOdd'], inline=True)
        embed.add_field(name='Mise max', value=f"{boost['maxBet']} €", inline=True)    

        formatted_time = french_time.strftime('%d/%m/%Y %H:%M:%S')
    
        embed.set_footer(text=f"Publié le {formatted_time} | {bookmaker.capitalize()}")

        boostCache = next((boostCache for boostCache in cache if boost["betId"] == boostCache["betId"]), None)
        
        if not boostCache:
            if channel:
                print(f"New boooost: {boost['intitule']} - {boost['startTime']}")

                message = await channel.send(f'{boost["intitule"]}\n\n<@&{roles[arobase]}>', embed=embed)
                mtMessage = await mtChannel.send('', embed=embed)

                if message is not None:
                    await message.edit(content=f'<@&{roles[arobase]}>', embed=embed)
                    thread = await message.create_thread(name=boost['intitule'][:96] + '...', auto_archive_duration=60)
                    # await thread.send('<@&1265314857889300523> Thread du nouveau boost', silent=True)
                    boost['message_id'] = message.id

                if boostsForum:
                    mtTags = [tag for tag in boostsForum.available_tags if tag.name == arobase]
                    mtPost = await boostsForum.create_thread(name=boost['intitule'][:96] + '...', auto_archive_duration=60, content=f'<@&{roles[arobase]}>', embed=embed, applied_tags=mtTags)
                    boost['mt_forum_thread_id'] = mtPost.thread.id
                    if MAIN_CHANNEL_ID == channel.id:
                        await tweet(boost, bookmaker)

                cache.append(boost)
            else:
                logging.warning(f"Channel not found: {channelId}")
        else:
            boost['message_id'] = boostCache['message_id']
            boost['mt_forum_thread_id'] = boostCache['mt_forum_thread_id']
            boostCache['startTime'] = boost['startTime']

            update_fields = ['boostedOdd', 'maxBet', 'title', 'intitule']
            # if boost != boostCache:
            if any(boost[el] != boostCache[el] for el in update_fields):
                cache.remove(boostCache)
                cache.append(boost)

                message = await channel.fetch_message(boostCache['message_id'])
                mtPost = boostsForum.get_thread(boostCache['mt_forum_thread_id'])

                await message.thread.send('Le boost a été modifié :', embed=embed)
                await mtPost.send('Le boost a été modifié :', embed=embed)
                mtMessage = await mtChannel.send('', embed=embed)

    try:
        with open(cache_file_path, 'w') as file:
            json.dump(cache, file, indent=4)
    except Exception as e:
        print(f"Error writing to cache file: {e}")
