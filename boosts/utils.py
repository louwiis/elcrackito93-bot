from boosts.winamax.script import winamax
# from boosts.unibet.unibet import unibet

cache_path='./boosts'

async def search_boosts(bot):
    await winamax(bot, cache_path);
    # await unibet(bot, cache_path);
