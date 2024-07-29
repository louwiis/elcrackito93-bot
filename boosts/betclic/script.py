import logging
import aiohttp
from datetime import datetime, timedelta
import pytz

logging.basicConfig(level=logging.INFO, filename='./boosts/betclic/log.log', format='%(asctime)s %(levelname)s:%(message)s')

async def betclic(bot):
    from boosts.utils import publish_boosts

    try:
        url = 'https://offer.cdn.begmedia.com/api/pub/v5/events/popular?application=2&categoryId=2_High-Football_High-Tennis_High-Rugby_High-MartialArts$$analytic_v2&countrycode=fr&language=fr&sitecode=frfr'
        headers = {
            "accept": "application/json",
            "accept-language": "en,en-GB;q=0.9,en-US;q=0.8,fr;q=0.7",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "Referer": "https://www.betclic.fr/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        finalBoosts = []

        async with aiohttp.ClientSession() as session:
            # get sports with boosts
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    response = await response.json()

                    for boost in response['boosted_odds']:       
                        finalBoosts.append({
                            'betId': boost['selection_id'],
                            'intitule': boost['selection_name'],
                            'boostedOdd': boost['odds'] if 'odds' in boost else 'N/A',
                            'odd': boost['previous_odds'] if 'previous_odds' in boost else 'N/A',
                            'title': boost['match_name'],
                            'bigBoost': True,
                            'maxBet': boost['max_stake'],
                            'sport': 'football',
                            'betAnalytixBetName': f"{boost['match_name']} / {boost['selection_name']}",
                            'startTime': boost['match_date_utc'].replace('Z', '+00:00')
                        })
                else:
                    print(f"Request failed with status: {response.status}")
                        
            await publish_boosts('betclic', bot, finalBoosts, '0xff0000')
        
    except Exception as e:
        print(f"Error fetching boosts: {e}")
