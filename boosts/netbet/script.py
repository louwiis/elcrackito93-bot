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
        url = 'https://ws.netbet.fr/component/datatree'
        headers = {
            "accept": "*/*",
            "accept-language": "en,en-GB;q=0.9,en-US;q=0.8,fr;q=0.7",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "cookie": "isMobileApp=false; isMobileAppEncapsulated=false; idaffiliation=6; affiliate_customs[searchEngine]=www.google.com; affiliate_customs[landingPage]=https://www.netbet.fr/; _scid=deff89e7-e261-462f-b771-f2a01bfaed9d; SSIDad6be59ed855041725de18219a49d3d8=25cctl8c3qvh5do03fs1pfgv2r; _hjSession_2908638=eyJpZCI6IjA4N2M5NTMzLTU5ZGMtNDhmYi1iM2MxLWQ5NWI5MjI1NzE2YiIsImMiOjE3MjE3NjkwNTE5NjksInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; _ScCbts=%5B%5D; _ga=GA1.2.517884063.1721769052; _gid=GA1.2.1212000468.1721769052; netbet-uf-session=ceq06pk3fhnabvhk7aj09du73g; _hjSessionUser_2908638=eyJpZCI6ImU2NjljZWNlLTNkZTMtNWZlMC1iMjVlLTkwMDNlZWViZGFjMCIsImNyZWF0ZWQiOjE3MjE3NjkwNTE5NjksImV4aXN0aW5nIjp0cnVlfQ==; _scid_r=deff89e7-e261-462f-b771-f2a01bfaed9d; cto_bundle=GyWIZl9aeUxzVHNxMDFXOVljSXR2RFFablpEM0RMcXlSQ2x3UEttazJkUzhaaEJRMkh2U0x6TFg2YWxmZjREMllqcDE4ZWdDUTE1THd2MDQzRlVMdFdPSk9DaU1haGxsQVBCSXJ5MnhMSkZoa0Rka0Q4TGloaGJLcUV6SWJCWW5kMlMlMkZKenBpcWViZ1hpcjlSZGZWclJTQW85dyUzRCUzRA; _uetsid=0aeaa870493811efba78f5a80e214c89; _uetvid=0aeab4f0493811ef80717bdfbc19feaf",
            "Referer": "https://www.netbet.fr/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        },
        body = {
            "context": {
                "url_key": "/super-cotes",
                "clientIp":"91.167.58.7",
                "version":"1.0.1",
                "device":"web_vuejs_desktop",
                "lang":"fr",
                "timezone":"Europe/Paris",
                "url_params": {}
            }
        }

        async with aiohttp.ClientSession() as session:
            # get sports with boosts
            async with session.post(url, headers=headers, json=body) as response:
                if response.status == 200:
                    response = await response.json()

                    print(response)
                else:
                    print(f"Request failed with status: {response.status}")
            
        await publish_boosts('pmu', bot, finalBoosts, '0xffA500')

    except Exception as e:
        logging.error(f"Error fetching Unibet boosts: {e}")
        return