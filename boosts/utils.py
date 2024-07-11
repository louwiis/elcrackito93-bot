from boosts.requests.winamax import winamax

cache_path='./boosts/cache.json'

async def search_boosts(bot):
    await winamax(bot, cache_path);
