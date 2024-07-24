import logging
import aiohttp # type: ignore
from datetime import datetime, timedelta
import re
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO, filename='./boosts/pmu/log.log', format='%(asctime)s %(levelname)s:%(message)s')

async def pmu(bot):
    from boosts.utils import publish_boosts

    try:
        finalBoosts = []
        sports = [];
        url = 'https://sports.pmu.fr/sportsbook/rest/v2/matches/?marketGroup=boost&featureType=boost&ln=fr'
        headers = {
            # "accept": "application/json, text/plain, */*",
            # "accept-language": "en,en-GB;q=0.9,en-US;q=0.8,fr;q=0.7",
            # "if-none-match": "512621865",
            # "priority": "u=1, i",
            # "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            # "sec-ch-ua-mobile": "?0",
            # "sec-ch-ua-platform": "\"macOS\"",
            # "sec-fetch-dest": "empty",
            # "sec-fetch-mode": "cors",
            # "sec-fetch-site": "same-site",
            # "Referer": "https://parisportif.pmu.fr/",
            # "Referrer-Policy": "origin",
            # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        },

        async with aiohttp.ClientSession() as session:
            # get sports with boosts
            async with session.get(url) as response:
                if response.status == 200:
                    response = await response.json()

                    # loop on response to get all sports
                    for league in response:
                        sports.append(league['sportId'])
                else:
                    print(f"Request failed with status: {response.status}")
            
            editedUrl = f'https://sports.pmu.fr/sportsbook/rest/v2/matches/?{"&".join([f"sportId={sport}" for sport in sports])}&marketGroup=boost&featureType=boost&ln=fr'

            print(editedUrl)
            # get boosts
            async with session.get(editedUrl) as response:
                if response.status == 200:
                    response = await response.json()

                    for event in response:
                        title = event['name'].split(' - SuperCote')[0]

                        if event['eventType'] == 'Tournament':
                            maxBetSearch = re.search(r'(\d{1,3}€ max)', event['name'])
                            maxBet = maxBetSearch.group(1).split('€')[0] if maxBetSearch else '?'
                            date = datetime.strptime(event['endDate'], '%Y-%m-%dT%H:%M:%S.%f+0000').replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Paris')).strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')
                        else:
                            date = datetime.strptime(event['startDate'], '%Y-%m-%dT%H:%M:%S.%f+0000').replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Paris')).strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')

                        for odd in event['odds'] if 'odds' in event else []:
                            for boost in odd['outcomes']:
                                if event['eventType'] == 'Match':
                                    maxBetSearch = re.search(r'(\d{1,3}€ max)', boost['outcome'])
                                    maxBet = maxBetSearch.group(1).split('€')[0] if maxBetSearch else '?'

                                finalBoosts.append({
                                    'betId': boost['id'],
                                    'intitule': boost['outcome'],
                                    'boostedOdd': boost['oddValue'],
                                    'odd': boost['wasPrice'],
                                    'title': title,
                                    'bigBoost': maxBet == '10',
                                    'maxBet': maxBet,
                                    'sport': 'football',
                                    'betAnalytixBetName': f"{title} / {boost['outcome']}",
                                    'startTime': date
                                })
                else:
                    print(f"Request failed with status: {response.status}")

        await publish_boosts('pmu', bot, finalBoosts, '0xffA500')

    except Exception as e:
        logging.error(f"Error fetching Unibet boosts: {e}")
        return