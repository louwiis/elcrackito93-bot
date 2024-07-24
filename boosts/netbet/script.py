import logging
import aiohttp # type: ignore
from datetime import datetime, timedelta
import re
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO, filename='./boosts/pmu/log.log', format='%(asctime)s %(levelname)s:%(message)s')

async def netbet(bot):
    from boosts.utils import publish_boosts

    try:
        url = 'https://ws.netbet.fr/component/datatree'
        headers = {
            "accept": "*/*",
            "accept-language": "en,en-GB;q=0.9,en-US;q=0.8,fr;q=0.7",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cookie": "isMobileApp=false; isMobileAppEncapsulated=false; idaffiliation=6; affiliate_customs[searchEngine]=www.google.com; affiliate_customs[landingPage]=https://www.netbet.fr/; _scid=deff89e7-e261-462f-b771-f2a01bfaed9d; SSIDad6be59ed855041725de18219a49d3d8=25cctl8c3qvh5do03fs1pfgv2r; _ScCbts=%5B%5D; _ga=GA1.2.517884063.1721769052; _gid=GA1.2.1212000468.1721769052; netbet-uf-session=ceq06pk3fhnabvhk7aj09du73g; _hjSessionUser_2908638=eyJpZCI6ImU2NjljZWNlLTNkZTMtNWZlMC1iMjVlLTkwMDNlZWViZGFjMCIsImNyZWF0ZWQiOjE3MjE3NjkwNTE5NjksImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_2908638=eyJpZCI6IjYxMTg5ODkzLTdkOGYtNDU0NS1hNDQxLTI5ZWE2MjFhY2IzNyIsImMiOjE3MjE3NzY1MjU3NDYsInMiOjEsInIiOjEsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; _uetsid=0aeaa870493811efba78f5a80e214c89; _uetvid=0aeab4f0493811ef80717bdfbc19feaf; _scid_r=deff89e7-e261-462f-b771-f2a01bfaed9d; cto_bundle=9RXXMF9aeUxzVHNxMDFXOVljSXR2RFFablpLVUpGWFBldXVmY0V5UTVaVWVNY0tZRmE3V0ozM1JMOVBaRjNjYWJPa0N4WmlpaiUyQlROOFhuOFZCNEtsMml4d2RQbVN5RzJKbVRMNXFSYUFyR2VSY0glMkY4OU9XWlRpNkQ4YXRLMm00eiUyQlN4d2E2YWRsJTJCUGl5QzMlMkJTcmRSOFN5d2xnJTNEJTNE",
            "origin": "https://www.netbet.fr",
            "priority": "u=1, i",
            "referer": "https://www.netbet.fr/",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
        links = []

        finalBoosts = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data='{"context":{"url_key":"/super-cotes/","device":"web_vuejs_desktop"}}', headers=headers) as response:
                if response.status == 200:
                    response = await response.json()

                    leftColumn = response['tree']['components'][next(i for i, item in enumerate(response['tree']['components']) if item["tree_compo_key"] == "left_column")]
                    menuSports = leftColumn['components'][next(i for i, item in enumerate(leftColumn['components']) if item["tree_compo_key"] == "menu_sport")]
                    superCotes = menuSports['data']['menu'][next(i for i, item in enumerate(menuSports['data']['menu']) if item["label"] == "Super Cotes")]

                    for section in superCotes['menu']:
                        for link in section['menu']:
                            links.append(link['url'])
                        
                else:
                    print(f"Request failed with status: {response.status}")

            for link in links:                
                async with session.post(url, data=f'{{"context": {{"url_key": "{link}", "clientIp": "91.167.58.7", "device": "web_vuejs_desktop"}}}}', headers=headers) as response:
                    if response.status == 200:
                        response = await response.json()

                        mainContentCompetition = response['tree']['components'][next(i for i, item in enumerate(response['tree']['components']) if item["tree_compo_key"] == "main_content_competition")]
                        finalWinner = mainContentCompetition['components'][next(i for i, item in enumerate(mainContentCompetition['components']) if item["tree_compo_key"] == "final_winner")]
                        events = finalWinner['data']['events']

                        for event in events:
                            if event['sport']['label'] == 'Super Cotes':
                                selections = event['markets'][0]['bets'][0]['selections']
                              
                                for selection in selections:
                                    if selection['odds_display'] != '-' and selection['odds'] != 1:
                                        finalBoosts.append({
                                            'betId': selection['id'],
                                            'intitule': event['label'],
                                            'boostedOdd': selection['odds'],
                                            'odd': '?',
                                            'title': event['category']['label'],
                                            'bigBoost': False,
                                            'maxBet': 25,
                                            'sport': 'football',
                                            'betAnalytixBetName': f"{event['category']['label']} / {event['label']}",
                                            'startTime': event['start']
                                        })

                    else:
                        response = await response.text()
                        print(f"Request failed with status: {response.status}")

        await publish_boosts('netbet', bot, finalBoosts, '0x343744')

    except Exception as e:
        logging.error(f"Error fetching Unibet boosts: {e}")
        return