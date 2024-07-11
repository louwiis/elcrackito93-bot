import discord
import requests
import re
import logging
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO, filename='./boosts/logs/winamax.log', format='%(asctime)s %(levelname)s:%(message)s')

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
            preloaded_state = preloaded_state_match.group(1)
            data = json.loads(preloaded_state)

            matches = data['matches'];
            boosts = data['bets'];
            outcomes = data['outcomes'];
            odds = data['odds'];

            finalBoosts = []

            boosts = [boost for boost in boosts.values() if 'previousOdd' in boost]

            for boost in boosts:
                betId = boost['betId']
                outcomeId = boost['outcomes'][0]

                match = [match for match in matches.values() if match['mainBetId'] == betId][0]

                boost['intitule'] = outcomes[f'{outcomeId}']['label']
                boost['odd'] = odds[f'{outcomeId}']
                boost['title'] = match['title'].split(':', 1)[1].strip()

                finalBoosts.append({
                    'intitule': boost['intitule'],
                    'boostedOdd': boost['odd'] if 'odd' in boost else 'N/A',
                    'odd': boost['previousOdd'] if 'previousOdd' in boost else 'N/A',
                    'title': boost['title'],
                    'bigBoost': boost['marketId'] != 9038,
                    'maxBet': boost['betTypeName'].lower().split('mise max ')[1].split(' €')[0],
                    'sport': 'football',
                    'betAnalytixBetName': f"{boost['title']} / {boost['intitule']}"
                })

            MAIN_CHANNEL_ID = int(os.getenv('WINAMAX_MAIN_CHANNEL_ID'))
            SECONDARY_CHANNEL_ID = int(os.getenv('WINAMAX_SECONDARY_CHANNEL_ID'))

            for boost in finalBoosts:
                with open(cache_path, 'r') as file:
                    cache = json.load(file).get('winamax', [])

                if boost not in cache:
                    if boost['bigBoost']:
                        channel = bot.get_channel(MAIN_CHANNEL_ID)
                    else:
                        channel = bot.get_channel(SECONDARY_CHANNEL_ID)

                    if channel:
                        embed = discord.Embed(
                            title=boost['title'],
                            description=boost['intitule'],
                            color=0xff0000 
                        )

                        embed.add_field(name='Côte initiale', value=boost['odd'], inline=True)
                        embed.add_field(name='Côte boostée', value=boost['boostedOdd'], inline=True)
                        embed.add_field(name='Mise max', value=boost['maxBet'], inline=True)

                        await channel.send(embed=embed)
                    else:
                        logging.warning(f"Channel not found: {MAIN_CHANNEL_ID if boost['bigBoost'] else SECONDARY_CHANNEL_ID}")
                    
            
            with open(cache_path, 'w') as file:
                json.dump({'winamax': finalBoosts}, file, indent=4)

        else:
            logging.warning("PRELOADED_STATE not found in the response.")

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")