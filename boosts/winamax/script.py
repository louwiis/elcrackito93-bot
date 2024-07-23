import requests
import re
import logging
import json
from datetime import datetime, timedelta
import pytz

logging.basicConfig(level=logging.INFO, filename='./boosts/winamax/log.log', format='%(asctime)s %(levelname)s:%(message)s')

async def winamax(bot):
    from boosts.utils import publish_boosts

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
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        preloaded_state_match = re.search(r'PRELOADED_STATE\s*=\s*({.*?});', response.text)
        if preloaded_state_match:
            preloaded_state = preloaded_state_match.group(1)
            data = json.loads(preloaded_state)

            matches = data['matches'] or {}
            boosts = data['bets'] or {}
            outcomes = data['outcomes'] or {}
            odds = data['odds'] or {}

            finalBoosts = []

            boosts = [boost for boost in boosts.values() if 'previousOdd' in boost]

            for boost in boosts:
                betId = boost['betId']
                outcomeId = boost['outcomes'][0]

                match = [match for match in matches.values() if match['mainBetId'] == betId][0] if matches else None

                if match:
                    boost['intitule'] = outcomes[f'{outcomeId}']['label']
                    boost['odd'] = odds[f'{outcomeId}']
                    boost['title'] = match['title'].split(':', 1)[1].strip()
                    boost['startTime'] = datetime.fromtimestamp(match['matchStart'])
                    
                    finalBoosts.append({
                        'betId': boost['betId'],
                        'intitule': boost['intitule'],
                        'boostedOdd': boost['odd'] if 'odd' in boost else 'N/A',
                        'odd': boost['previousOdd'] if 'previousOdd' in boost else 'N/A',
                        'title': boost['title'],
                        'bigBoost': boost['marketId'] != 9038,
                        'maxBet': boost['betTypeName'].lower().split('mise max ')[1].split(' €')[0],
                        'sport': 'football',
                        'betAnalytixBetName': f"{boost['title']} / {boost['intitule']}",
                        'startTime': boost['startTime'].astimezone(pytz.utc).isoformat()
                    })
                else:
                    logging.warning(f"Match not found for betId {betId}")
            
            await publish_boosts('winamax', bot, finalBoosts, '0xff0000')

        else:
            logging.warning("PRELOADED_STATE not found in the response.")

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")