import logging
import aiohttp # type: ignore
from datetime import datetime, timedelta
import re
import json
import pytz

cache_file_path = './boosts/pselZebet/cache.json'

# Configure logging
logging.basicConfig(level=logging.INFO, filename='./boosts/pselZebet/log.log', format='%(asctime)s %(levelname)s:%(message)s')

def get_boosts(response, finalBoosts):
    if 'items' in response:
        for id in response['items']:
            if id.startswith('m'):
                boost = response['items'][id]
                match = response['items'][boost['parent']]
                boostedBet = [odd for odd in response['items'].values() if odd['parent'] == id and 'flags' not in odd][0]

                odd = boost['desc'].split('→')[0].split('(')[-1].split(' ')[0] if '→' in boost['desc'] else boost['desc'].split('->')[0].split('(')[-1].split(' ')[0]

                if '€' in boost['desc'] and 'mise max' in boost['desc'].lower():
                    maxBet = boost['desc'].lower().split('mise max ')[1].split('€')[0].strip()                                      

                    finalBoosts.append({
                        'matchId': boost['parent'],
                        'betId': id,
                        'title': match['desc'],
                        'intitule': boost['desc'].split(' (')[0].strip() + ' / ' + boostedBet['desc'] + ' / ' + boost['period'],
                        'boostedOdd': boostedBet['price'],
                        'odd': odd,
                        'bigBoost': maxBet == '10',
                        'maxBet': maxBet,
                        'sport': match['path']['Sport'],
                        'betAnalytixBetName': boost['desc'] + ' / ' + boostedBet['desc'],
                        'startTime': convert_to_iso(match['start'])
                    })

async def pselZebet(bot):
    from boosts.utils import publish_boosts

    url = 'https://www.enligne.parionssport.fdj.fr/lvs-api/next/50/p58245556,p58429681,p58421879,p58422124,p58450232,p58557545,p58425119,p58422320,p58422324,p58406581,p58499583,p58470484,p58421212,p58559769,p58559623,p58429444,p58416562,p58474788,p58598438,p58712243?lineId=1&originId=3&breakdownEventsIntoDays=true&pageIndex=0&showPromotions=true'
    headers = {
        'Accept': 'application/json, text/plain, /',
        'Accept-Language': 'en,en-GB;q=0.9,en-US;q=0.8,fr;q=0.7',
        'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'X-Lvs-Hstoken': 'uaB05pvXPkBjNs6Zlb1h1S9wJKQgI6i4yfA6VcEjXTFbFCCCVFHlPc2mUXPbAuEpwBvQyIvKoP1n3apSj3MGiIFvX6P_jprXEwLkJ0d3A-yWBQRclW9yVT1ZNUhWuFjndCNw_scdnwVoAqU0cNf5Yg==',
        "cookie": "pa_privacy=%22optin%22; abp-pselw=1065943818.41733.0000; TCPID=12311502359236305494; TC_PRIVACY_PSEL=0%40045%7C14%7C1881%408%2C9%2C10%40%401700177040508%2C1700177040508%2C1715729040508%40; TC_PRIVACY_PSEL_CENTER=8%2C9%2C10; _pcid=%7B%22browserId%22%3A%22lp1tievyej3l3fun%22%2C%22_t%22%3A%22m4q8fxq7%7Clp1tige7%22%7D; pa_vid=%22lp1tievyej3l3fun%22; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXSwH18yBbACwBHABwAzAB7DWAH1QAHAIz56AcyjsAvkA; _pcus=eyJ1c2VyU2VnbWVudHMiOm51bGwsIl90IjoibTRxOGZ5YnV8bHAxdGlnenUifQ%3D%3D; iadvize-4635-consent=true; iadvize-4635-vuid=%7B%22vuid%22%3A%2291aab922b2b12b83a40dfada7de5fcb2655d0895efab8%22%2C%22deviceId%22%3A%22759759ad-b075-4cf0-bb57-7d53a515ee2f%22%7D; _pcid=%7B%22browserId%22%3A%22lp1tievyej3l3fun%22%2C%22_t%22%3A%22m4q8fxq7%7Clp1tige7%22%7D; _pcus=eyJ1c2VyU2VnbWVudHMiOm51bGwsIl90IjoibTRxOGZ5YnV8bHAxdGlnenUifQ%3D%3D; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXSwH18yBbACwBHABwAzAB7DWAH1QAHAIz56AcyjsAvkA; pa_vid=%22lp1tievyej3l3fun%22; device_view=full",
        "Referer": "https://www.enligne.parionssport.fdj.fr/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    try:
        finalBoosts = []

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    response = await response.json()

                    get_boosts(response, finalBoosts)

                else:
                    print(f"Request failed with status: {response.status}")


            utc_time = datetime.now(pytz.utc)

            try:
                with open(cache_file_path, 'r') as file:
                    cache = [boost for boost in json.load(file) if datetime.fromisoformat(boost['startTime']).replace(tzinfo=pytz.utc) > utc_time - timedelta(hours=12)]

            except FileNotFoundError:
                cache = []

            except Exception as e:
                print(f"Error reading cache file: {e}")
                cache = []

            for boost in cache:

                async with session.get(f'https://www.enligne.parionssport.fdj.fr/lvs-api/ff/{boost["matchId"]}?lineId=1&originId=3&ext=1&showPromotions=true&showMarketTypeGroups=true', headers=headers) as response:
                    if response.status == 200:
                        response = await response.json()

                        get_boosts(response, finalBoosts)

                    else:
                        print(f"Request failed with status: {response.status}")


        finalBoosts = [dict(t) for t in {tuple(d.items()) for d in finalBoosts}]
        await publish_boosts('pselZebet', bot, finalBoosts, '0x0000ff')

    except Exception as e:
        logging.error(f"Error fetching Psel boosts: {e}")
        return


def convert_to_iso(input_str):
    pattern = r"(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})"

    match = re.match(pattern, input_str)
    if match:
        year = "20" + match.group(1)
        month = match.group(2)
        day = match.group(3)
        hour = match.group(4)
        minute = match.group(5)
        
        dt = datetime.strptime(f"{year} {month} {day} {hour} {minute}", "%Y %m %d %H %M")
        
        return (dt).isoformat()
    else:
        return None