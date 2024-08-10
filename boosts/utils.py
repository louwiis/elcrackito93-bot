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

async def search_boosts(bot):
    await winamax(bot)
    await unibet(bot)
    await pselZebet(bot)
    await pmu(bot)
    await netbet(bot)
    await betclic(bot)

async def publish_boosts(bookmaker, bot, finalBoosts, color):
    MAIN_CHANNEL_ID = int(os.getenv(f'{bookmaker.upper()}_MAIN_CHANNEL_ID'))
    MT_MAIN_CHANNEL_ID = int(os.getenv(f'MT_{bookmaker.upper()}_MAIN_CHANNEL_ID'))
    SECONDARY_CHANNEL_ID = int(os.getenv(f'{bookmaker.upper()}_SECONDARY_CHANNEL_ID'))
    MT_SECONDARY_CHANNEL_ID = int(os.getenv(f'MT_{bookmaker.upper()}_SECONDARY_CHANNEL_ID'))
    FORUM_CHANNEL_ID = int(os.getenv(f'BOOSTS_FORUM_CHANNEL_ID'))
    
    cache_file_path = os.path.join(os.getcwd(), cache_path, bookmaker, 'cache.json')

    utc_time = datetime.now(pytz.utc)
    french_time = utc_time.astimezone(pytz.timezone('Europe/Paris'))
    formatted_time = french_time.strftime('%d/%m/%Y %H:%M:%S')
    
    try:
        with open(cache_file_path, 'r') as file:
            cache = [boost for boost in json.load(file) if datetime.fromisoformat(boost['startTime']).replace(tzinfo=pytz.utc) > utc_time - timedelta(hours=12)]

    except FileNotFoundError:
        cache = []

    except Exception as e:
        print(f"Error reading cache file: {e}")
        cache = []

    for boost in finalBoosts:
        embed = discord.Embed(
            title=boost['title'],
            description=boost['intitule'],
            color=int(color, 16)
        )

        embed.add_field(name='Côte initiale', value=boost['odd'], inline=True)
        embed.add_field(name='Côte boostée', value=boost['boostedOdd'], inline=True)
        embed.add_field(name='Mise max', value=f"{boost['maxBet']} €", inline=True)    

        formatted_time = french_time.strftime('%d/%m/%Y %H:%M:%S')

        embed.set_footer(text=formatted_time)

        boostCache = next((boostCache for boostCache in cache if boost["betId"] == boostCache["betId"]), None)
        
        channelId = MAIN_CHANNEL_ID if boost['bigBoost'] else SECONDARY_CHANNEL_ID            
        mtChannelId = MT_MAIN_CHANNEL_ID if boost['bigBoost'] else MT_SECONDARY_CHANNEL_ID
        channel = bot.get_channel(channelId)
        mtChannel = bot.get_channel(mtChannelId)
        boostsForum = bot.get_channel(FORUM_CHANNEL_ID)

        if not boostCache:
            if channel:
                # print(f"New boooost: {boost['intitule']} - {boost['startTime']}")

                message = await channel.send(f'{boost["intitule"]}', embed=embed)
                await message.edit(content='', embed=embed)
                thread = await message.create_thread(name=boost['intitule'][:96] + '...', auto_archive_duration=60)
                # await thread.send('<@&1265314857889300523> Thread du nouveau boost', silent=True)
                boost['message_id'] = message.id
                cache.append(boost)

                if MAIN_CHANNEL_ID == channel.id:
                    await tweet(boost, bookmaker)
            else:
                logging.warning(f"Channel not found: {channelId}")

            if mtChannel:
                message = await mtChannel.send(f'{boost["intitule"]}', embed=embed)
                await message.edit(content='', embed=embed)
                thread = await message.create_thread(name=boost['intitule'][:96] + '...', auto_archive_duration=60)
                # await thread.send('<@&1265314857889300523> Thread du nouveau boost', silent=True)
                boost['mt_message_id'] = message.id
            else:
                logging.warning(f"Channel not found: {mtChannelId}")

            if boostsForum:
                tags = [tag for tag in boostsForum.available_tags if tag.name == bookmaker]
                post = await boostsForum.create_thread(name=boost['intitule'][:96] + '...', auto_archive_duration=60, embed=embed, applied_tags=tags)
                boost['forum_thread_id'] = post.thread.id
            
        else:
            boost['message_id'] = boostCache['message_id']
            boost['mt_message_id'] = boostCache['mt_message_id']
            boost['forum_thread_id'] = boostCache['forum_thread_id']
            boostCache['startTime'] = boost['startTime']

            update_fields = ['boostedOdd', 'maxBet', 'title', 'intitule']
            # if boost != boostCache:
            if any(boost[el] != boostCache[el] for el in update_fields):
                cache.remove(boostCache)
                cache.append(boost)

                message = await channel.fetch_message(boostCache['message_id'])
                mtMessage = await mtChannel.fetch_message(boostCache['mt_message_id'])
                post = boostsForum.get_thread(boostCache['forum_thread_id'])

                await message.thread.send('Le boost a été modifié :', embed=embed)
                await mtMessage.thread.send('Le boost a été modifié :', embed=embed)
                await post.send('Le boost a été modifié :', embed=embed)

    try:
        with open(cache_file_path, 'w') as file:
            json.dump(cache, file, indent=4)
    except Exception as e:
        print(f"Error writing to cache file: {e}")
