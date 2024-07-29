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


# const tweet = async (boost, bookmakerName) => {
#   try {
#     console.log(`🚀🔥 Nouveau boooost ${bookmakerName.charAt(0).toUpperCase() + bookmakerName.slice(1).toLowerCase()} !\n\n📍 ${boost.title}\n📝 ${boost.description}\n\n📈 ${boost.odd !== '?' ? boost.odd + ' ->' : ''} ${boost.boostedOdd}\n💰 ${boost.maxBet}€ max\n\n❤️ si tu prends !\n\n#TeamParieur #Boost #${bookmakerName.charAt(0).toUpperCase() + bookmakerName.slice(1).toLowerCase()}`)
#     await twitterClient.v2.tweet({text: `🚀🔥 Nouveau boooost ${bookmakerName.charAt(0).toUpperCase() + bookmakerName.slice(1).toLowerCase()} !\n\n📍 ${boost.title}\n📝 ${boost.description}\n\n📈 ${boost.odd !== '?' ? boost.odd + ' ->' : ''} ${boost.boostedOdd}\n💰 ${boost.maxBet}€ max\n\n❤️ si tu prends !\n\n#TeamParieur #Boost #${bookmakerName.charAt(0).toUpperCase() + bookmakerName.slice(1).toLowerCase()}`, });
#   } catch (e) {
#     console.log(e);
#   }
# }

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
        # response = client.create_tweet(text=tweet_text)
        # print("Tweet sent successfully!", response)
    except Exception as e:
        print(e)