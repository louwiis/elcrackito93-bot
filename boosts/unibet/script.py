import discord
import requests
import re
import logging
import json
import os
import aiohttp
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, filename='./boosts/unibet/log.log', format='%(asctime)s %(levelname)s:%(message)s')

async def unibet(bot):
    from boosts.utils import publish_boosts

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
    }

    try:
        finalBoosts = []

        async with aiohttp.ClientSession() as session:
            # flash boosts
            url = "https://www.unibet.fr/zones/mainheadlines.json?pageId=200"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    response = await response.json()

                    for item in response['mainheadlines_first']:
                        bet = item['market']['selections'][0]

                        if bet['flashBet'] == True:
                            bet = item['market']['selections'][0]
                            boostedOdd = (100 + float(bet['currentPriceUp']) * (100 / float(bet['currentPriceDown']))) / 100

                            finalBoosts.append({
                                'intitule': bet['name'],
                                'title': f"{item['marketName']} - {item['shortTitle']}",
                                'description': bet['name'],
                                'bigBoost': True,
                                'odd': bet['originalOdd'],
                                'boostedOdd': boostedOdd,
                                'maxBet': 10,
                                'sport': 'football',
                                'betAnalytixBetName': f"{item['shortTitle']} / {bet['name']}",
                                'startTime': datetime.fromtimestamp(item['eventStartDate'] / 1000)
                            })
                else:
                    print(f"Request failed with status: {response.status}")

            # classic boosts
            url = "https://www.unibet.fr/zones/v3/sportnode/markets.json?nodeId=703695152&filter=Super%2520Cote%2520Boost%25C3%25A9e&marketname=Super%2520Cote%2520Boost%25C3%25A9e%2520(50%25E2%2582%25AC%2520max)"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    response = await response.json()

                    days = response['marketsByType'][0]['days']

                    for day in days:
                        for event in day['events']:
                            for market in event['markets']:
                                for selection in market['selections']:
                                    boostedOdd = (100 + float(selection['currentPriceUp']) * (100 / float(selection['currentPriceDown']))) / 100

                                    finalBoosts.append({
                                        'title': market['eventName'],
                                        'intitule': selection['name'],
                                        'bigBoost': False,
                                        'odd': selection['originalOdd'],
                                        'boostedOdd': boostedOdd,
                                        'maxBet': 50,
                                        'sport': event['cmsSportName'],
                                        'betAnalytixBetName': f"{market['eventName']} / {selection['name']}",
                                        'startTime': (datetime.fromtimestamp(event['eventStartDate'] / 1000) + timedelta(hours=1)).isoformat(),
                                    })
                else:
                    print(f"Request failed with status: {response.status}")

        await publish_boosts('unibet', bot, finalBoosts, '0x00ff00')

    except Exception as e:
        logging.error(f"Error fetching Unibet boosts: {e}")
        return
