import discord
import logging
import json
import os
from datetime import datetime, timedelta
import pytz

from boosts.winamax.script import winamax
from boosts.unibet.script import unibet
from boosts.psel.script import psel

cache_path = 'boosts'

async def search_boosts(bot):
    await winamax(bot)
    await unibet(bot)
    await psel(bot)

async def publish_boosts(bookmaker, bot, finalBoosts, color):
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

        embed.set_footer(text=formatted_time)

        boostCache = next((boostCache for boostCache in cache if boost["betId"] == boostCache["betId"]), None)
        
        if not boostCache:
            channel = bot.get_channel(MAIN_CHANNEL_ID if boost['bigBoost'] else SECONDARY_CHANNEL_ID)

            if channel:
                message = await channel.send(embed=embed)
                boost['message_id'] = message.id
                cache.append(boost)
            else:
                logging.warning(f"Channel not found: {MAIN_CHANNEL_ID if boost['bigBoost'] else SECONDARY_CHANNEL_ID}")
        else:
            boost['message_id'] = boostCache['message_id']
            boostCache['startTime'] = boost['startTime']

            # update_fields = ['odd', 'boostedOdd', 'maxBet', 'title']
            # if any(boost[el] != boostCache[el] for el in update_fields):
            if boost != boostCache:
                cache.remove(boostCache)
                cache.append(boost)

                channel = bot.get_channel(MAIN_CHANNEL_ID if boost['bigBoost'] else SECONDARY_CHANNEL_ID)
                message = await channel.fetch_message(boostCache['message_id'])

                if message.thread is None:
                    thread = await message.create_thread(name='Thread de discussion sur le boost', auto_archive_duration=60)
                else:
                    thread = message.thread

                await thread.send('Le boost a été modifié !', embed=embed)

    try:
        with open(cache_file_path, 'w') as file:
            json.dump(cache, file, indent=4)
    except Exception as e:
        print(f"Error writing to cache file: {e}")
