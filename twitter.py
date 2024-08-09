from tweepy import Client
import os

TWITTER_APP_ID=1696203009875755014
client = Client(
    bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
)

async def tweet(boost, bookmaker_name):
    try:
        tweet_text = (
            f"🚀🔥 Nouveau boooost {bookmaker_name.capitalize()} !\n\n"
            f"📍 {boost['title']}\n"
            f"📝 {boost['intitule']}\n\n"
            f"📈 {boost['odd'] if boost['odd'] != '?' else ''} -> {boost['boostedOdd']}\n"
            f"💰 {boost['maxBet']}€ max\n\n"
            f"❤️ si tu prends !\n\n"
            f"#TeamParieur #Boost #{bookmaker_name.capitalize()}"
        )
        print("Tweeting:", tweet_text)
        response = client.create_tweet(text=tweet_text)
        print("Tweet sent successfully!", response)
    except Exception as e:
        print(e)