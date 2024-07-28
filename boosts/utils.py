import discord
import logging
import json
import os
from datetime import datetime, timedelta
import pytz

from boosts.winamax.script import winamax
from boosts.unibet.script import unibet
from boosts.psel.script import psel
from boosts.pmu.script import pmu
from boosts.netbet.script import netbet

from twitter import tweet

cache_path = 'boosts'

async def search_boosts(bot):
    # await winamax(bot)
    await unibet(bot)
    # await psel(bot)
    # await pmu(bot)
    # await netbet(bot)

async def publish_boosts(bookmaker, bot, finalBoosts, color):
    print(f"Publishing {len(finalBoosts)} boosts from {bookmaker}")
    MAIN_CHANNEL_ID = int(os.getenv(f'{bookmaker.upper()}_MAIN_CHANNEL_ID'))
    SECONDARY_CHANNEL_ID = int(os.getenv(f'{bookmaker.upper()}_SECONDARY_CHANNEL_ID'))
    
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

        print(f"Boost: {boost['intitule']} - {boost['startTime']} - {formatted_time}")

        embed.set_footer(text=formatted_time)

        boostCache = next((boostCache for boostCache in cache if boost["betId"] == boostCache["betId"]), None)
        
        if not boostCache:
            channel = bot.get_channel(MAIN_CHANNEL_ID if boost['bigBoost'] else SECONDARY_CHANNEL_ID)

            if channel:
                message = await channel.send(f'{boost["intitule"]}', embed=embed)
                await message.edit(content='', embed=embed)
                thread = await message.create_thread(name=boost['intitule'][:96] + '...', auto_archive_duration=60)
                await thread.send('<@&1265314857889300523> Thread du nouveau boost', silent=True)
                boost['message_id'] = message.id
                cache.append(boost)

                if MAIN_CHANNEL_ID == channel.id:
                    await tweet(boost, bookmaker)
            else:
                logging.warning(f"Channel not found: {MAIN_CHANNEL_ID if boost['bigBoost'] else SECONDARY_CHANNEL_ID}")
        else:
            boost['message_id'] = boostCache['message_id']
            boostCache['startTime'] = boost['startTime']

            update_fields = ['boostedOdd', 'maxBet', 'title', 'intitule']
            # if boost != boostCache:
            if any(boost[el] != boostCache[el] for el in update_fields):
                cache.remove(boostCache)
                cache.append(boost)

                channel = bot.get_channel(MAIN_CHANNEL_ID if boost['bigBoost'] else SECONDARY_CHANNEL_ID)
                message = await channel.fetch_message(boostCache['message_id'])

                await message.thread.send('Le boost a été modifié :', embed=embed)

    try:
        with open(cache_file_path, 'w') as file:
            json.dump(cache, file, indent=4)
    except Exception as e:
        print(f"Error writing to cache file: {e}")
