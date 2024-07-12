import discord
import requests
import re
import logging
import json
import os
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, filename='./boosts/winamax/log.log', format='%(asctime)s %(levelname)s:%(message)s')

async def winamax(bot, cache_path):
    url = 'https://www.winamax.fr/paris-sportifs/sports/100000'
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en,en-GB;q=0.9,en-US;q=0.8,fr;q=0.7",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    }

    try:
        # so there is a 
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Extract PRELOAD_STATE from the response text
        preloaded_state_match = re.search(r'PRELOADED_STATE\s*=\s*({.*?});', response.text)
        if preloaded_state_match:
            # preloaded_state = preloaded_state_match.group(1)
            # data = json.loads(preloaded_state)

            # matches = data['matches'];
            # boosts = data['bets'];
            # outcomes = data['outcomes'];
            # odds = data['odds'];

            # finalBoosts = []

            # boosts = [boost for boost in boosts.values() if 'previousOdd' in boost]

            # for boost in boosts:
            #     betId = boost['betId']
            #     outcomeId = boost['outcomes'][0]

            #     match = [match for match in matches.values() if match['mainBetId'] == betId][0]

            #     boost['intitule'] = outcomes[f'{outcomeId}']['label']
            #     boost['odd'] = odds[f'{outcomeId}']
            #     boost['title'] = match['title'].split(':', 1)[1].strip()
            #     boost['startTime'] = datetime.fromtimestamp(match['matchStart'])

            #     finalBoosts.append({
            #         'intitule': boost['intitule'],
            #         'boostedOdd': boost['odd'] if 'odd' in boost else 'N/A',
            #         'odd': boost['previousOdd'] if 'previousOdd' in boost else 'N/A',
            #         'title': boost['title'],
            #         'bigBoost': boost['marketId'] != 9038,
            #         'maxBet': boost['betTypeName'].lower().split('mise max ')[1].split(' €')[0],
            #         'sport': 'football',
            #         'betAnalytixBetName': f"{boost['title']} / {boost['intitule']}",
            #         'startTime': boost['startTime'].isoformat(),
            #     })

            MAIN_CHANNEL_ID = int(os.getenv('WINAMAX_MAIN_CHANNEL_ID'))
            SECONDARY_CHANNEL_ID = int(os.getenv('WINAMAX_SECONDARY_CHANNEL_ID'))

            # try:
                # with open(f'{cache_path}/winamax/cache2.json', 'r') as file:
                    # date = datetime.now().isoformat()
                    # finalBoosts = json.load(file)

            # except FileNotFoundError:
                # cache = []

            try:
                with open(f'{cache_path}/winamax/cache.json', 'r') as file:
                    date = datetime.now().isoformat()
                    cache = json.load(file)

                    for boost in cache:
                        if datetime.fromisoformat(date) > datetime.fromisoformat(boost['startTime']):
                            channel = bot.get_channel(MAIN_CHANNEL_ID if boost['bigBoost'] else SECONDARY_CHANNEL_ID)
                            message = await channel.fetch_message(boost['message_id'])
                            await message.delete()
                            cache.remove(boost)
                    
            except FileNotFoundError:
                cache = []

            for boost in finalBoosts:
                embed = discord.Embed(
                    title=boost['title'],
                    description=boost['intitule'],
                    color=0xff0000 
                )

                embed.add_field(name='Côte initiale', value=boost['odd'], inline=True)
                embed.add_field(name='Côte boostée', value=boost['boostedOdd'], inline=True)
                embed.add_field(name='Mise max', value=boost['maxBet'], inline=True)

                boostCache = next((boostCache for boostCache in cache if boost["intitule"] == boostCache["intitule"]), None)
                
                if not boostCache:
                    if boost['bigBoost']:
                        channel = bot.get_channel(MAIN_CHANNEL_ID)
                    else:
                        channel = bot.get_channel(SECONDARY_CHANNEL_ID)

                    if channel:
                        message = await channel.send(embed=embed)

                        boost['message_id'] = message.id
                        cache.append(boost)
                    else:
                        logging.warning(f"Channel not found: {MAIN_CHANNEL_ID if boost['bigBoost'] else SECONDARY_CHANNEL_ID}")
                else:
                    boost['message_id'] = boostCache['message_id']

                    list = [
                        'odd',
                        'boostedOdd',
                        'maxBet',
                        'title',
                    ]

                    if any(boost[el] != boostCache[el] for el in list):
                        cache.remove(boostCache)
                        cache.append(boost)

                        channel = bot.get_channel(MAIN_CHANNEL_ID if boost['bigBoost'] else SECONDARY_CHANNEL_ID)
                        message = await channel.fetch_message(boostCache['message_id'])

                        if not message.thread:
                            thread = await message.create_thread(name=f'Thread de discussion sur le boost', auto_archive_duration=60)
                        else: 
                            thread = message.thread

                        await thread.send('Le boost a été modifié !', embed=embed)

            with open(f'{cache_path}/winamax/cache.json', 'w') as file:
                json.dump(cache, file, indent=4)

        else:
            logging.warning("PRELOADED_STATE not found in the response.")

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")