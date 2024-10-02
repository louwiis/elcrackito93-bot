import discord
from discord.ext import tasks
from discord import app_commands
from discord import ButtonStyle, ui, Message, Interaction

import aiohttp
from datetime import datetime

import sys
import os
from dotenv import load_dotenv
load_dotenv()

from boosts.utils import search_boosts

print(discord.__version__)

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
MT_SERVER_ID = os.getenv('MT_SERVER_ID')


# @tree.command(
#     name="ping",
#     description="My first application Command",
#     guild=discord.Object(id=SERVER_ID)
# )
# async def first_command(interaction):
#     await interaction.response.send_message("Pong!", ephemeral=True)

@bot.event
async def on_message(message):
    if message.type == discord.MessageType.thread_created:
        try:
            await message.delete()
        except:
            print('Error deleting message')
            pass

@tasks.loop(seconds=15)
async def boosts():
    await search_boosts(bot)

# create a slashcommands function that will return the diffenrece in % between two numbers in params
@tree.command(
    name="value",
    description="Calcul de value et de mise en privé",
    guild=discord.Object(id=MT_SERVER_ID)
)
async def value(interaction, trueodds: float, taken_odds: float):
    value = (taken_odds - trueodds) / trueodds * 100 
    kelly = value / (taken_odds - 1)


    # make a message to show the percentage value and the 4 types of kelly
    # make an embed it will be easier

    embed = discord.Embed(
        title=f"Calcul de value et de mise",
        description=f"Trueodds: {trueodds}\nCote prise: {taken_odds}\nValue est de {value:.2f}%",
        color=0xFFFFFF
    )

    embed.add_field(name="Kelly/2", value=f"{kelly/2:.2f}%", inline=True)
    embed.add_field(name="Kelly/3", value=f"{kelly/3:.2f}%", inline=True)
    embed.add_field(name="Kelly/4", value=f"{kelly/4:.2f}%", inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(
    name="public_value",
    description="Crée un post public avec le calcul de value et de mise",
    guild=discord.Object(id=MT_SERVER_ID)
)
async def public_value(interaction, trueodds: float, taken_odds: float):
    value = (taken_odds - trueodds) / trueodds * 100 
    kelly = value / (taken_odds - 1)

    embed = discord.Embed(
        title=f"Calcul de value et de mise",
        description=f"Trueodds: {trueodds}\nCote prise: {taken_odds}\nValue: {value:.2f}%",
        color=0xFFFFFF
    )

    embed.add_field(name="Kelly/2", value=f"{kelly/2:.2f}%", inline=True)
    embed.add_field(name="Kelly/3", value=f"{kelly/3:.2f}%", inline=True)
    embed.add_field(name="Kelly/4", value=f"{kelly/4:.2f}%", inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=False)    

@tree.command(
    name="bet",
    description="Crée un bet dans le bet analytix MoneyTime",
    guild=discord.Object(id=MT_SERVER_ID)
)
async def bet(interaction, titre: str, cote: float, mise: float, sport: str, bookmaker: str, pourcentage: bool = True):
    print(titre, cote, mise, sport, bookmaker, pourcentage)

    async with aiohttp.ClientSession() as session:
        bookmakers = {
            '1xbet': 25,
            'betclic': 2,
            'parionssport': 8,
            'pmu': 9,
            'unibet': 10,
            'winamax': 11,
            'zebet': 12,
            'pinnacle': 245,
        }

        sports = {
            'football': 1,
            'tennis': 2,
            'basketball': 3,
            'rugby': 4,
            'handball': 5,
            'volleyball': 6,
            'hockey': 7,
            'baseball': 8,
            'american_football': 9,
            'futsal': 10,
        }

        headers = {
            "accept": "application/json",
            "accept-language": "en,en-GB;q=0.9,en-US;q=0.8,fr;q=0.7",
            "app": "mobileBax",
            "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiYXgiLCJ1aWQiOjM5NTA1NywicHNldWRvIjoiTG91d2lzIiwicHJlbWl1bSI6MTcyODE1MzUwMiwiYmF4QXV0aFNlY3VyaXR5IjoiNU5LU1BvNGFDN1dmcERFZDRGclh4bjMxaGUxTk5aTHpaRW9yekhIcWlWRDFyajFOZDdYd0tJOHhsbjNDbHVVRnhKbTFYbjNSbjFvMDFyampsZE91RmwyN2d4dHVNdnFGZDg4cUtzRkZHRXlHYVZieFBPUDZQc1VXVWRSa0Y4Z1V6OFdibm5mSkVnUE9kd3B3aGhkZmIzZVBSQUlOQ1dZS0NPaWVvZ3FXc0RpVFp6VTJaTEcxWVJtbFh4dDFIUFhkaVQzM3BMcWZRNVVzbWh5aUF4SDBQNGpZa2JNZ29lQmd2TzZXdFNHR1V2aTFjMFdFMHJJbmRTRHJGZFhlVXpMIiwiaWF0IjoxNzI3ODI4MDQzLCJleHAiOjE3MzU3MTIwNDN9.Pfnm0Wkk3yBTWx4lZ7tITG0ormyqMf2eVFSFyP4XbVs",
            "content-type": "application/json;charset=UTF-8",
            "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sid": "152120",
            "Referer": "https://app.bet-analytix.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        body = {
            "id": None,
            "date": datetime.now().isoformat(),
            "bankroll": 50,
            "bookmaker": None,
            "tipster": 0,
            "category": 0,
            "competition": 0,
            "betType": 0,
            "sport": 1,
            "label": titre,
            "odd": cote,
            "stake": mise,
            "live":0,
            "freebet":0,
            "cashout":0,
            "gainCashout": None,
            "masked":0,
            "state":0,
            "bonus":0,
            "gainBonus": None,
            "comment": '',
            "commission": 0,
            "priceCommission": None,
            "eachway": 0,
            "gainEachway": None,
            "closing": None,
            "canApplyCommission": True,
            "prout":21,
            "bets": [
                {
                    "sport":1,
                    "label":"",
                    "odd": None,
                    "state":0,
                    "competition": None,
                    "betType": None,
                    "closing": None,
                    "moreInformationsVisible": False
                },
                {
                    "sport":1,
                    "label":"",
                    "odd": None,
                    "state":0,
                    "competition": None,
                    "betType": None,
                    "closing": None,
                    "moreInformationsVisible": False
                }
            ],
            "betsValid":0,
            "system": None,
            "type":1
        }

        # if sport doesn't exist in the sports dict, we set it to 1
        if sport in sports:
            body['sport'] = sports[sport]
        if bookmaker in bookmakers:
            body['bookmaker'] = bookmakers[bookmaker]

        if pourcentage:
            async with session.get("https://api.bet-analytix.com/bankrolls", headers=headers) as response:
                if response.status == 200:
                    response = await response.json()
                    bankrolls = response['data']

                    for bankroll in bankrolls:
                        if bankroll['id_bankroll'] == 50:
                            body['stake'] = bankroll['capital_actuelle'] * mise / 100

                            async with session.post("https://api.bet-analytix.com/bet/simple", headers=headers, json=body) as response:
                                if response.status == 200:
                                    response = await response.json()
                                    print(response)
                                else:
                                    print(f"Request failed with status: {response}")
                            
                else:
                    print(f"Request failed with status: {response.status}")
        else:
            async with session.post("https://api.bet-analytix.com/bet/simple", headers=headers, json=body) as response:
                if response.status == 200:
                    response = await response.json()
                    print(response)
                else:
                    print(f"Request failed with status: {response.status}")

    
    # create an embed
    embed = discord.Embed(
        title=f"Nouveaux bet ajouté",
        description=f"Voici les détails du bet ajouté :",
        color=0xFFFFFF
    )

    embed.add_field(name="Titre", value=titre, inline=True)
    embed.add_field(name="Cote", value=cote, inline=True)
    embed.add_field(name="Mise", value=mise, inline=True)
    embed.add_field(name="Sport", value=sport, inline=True)
    embed.add_field(name="Bookmaker", value=bookmaker, inline=True)
    embed.add_field(name="Pourcentage", value=pourcentage, inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=False)

@bot.event
async def on_ready():
    # await tree.sync(guild=discord.Object(id=SERVER_ID))
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    boosts.start()

    await tree.sync(guild=discord.Object(id=MT_SERVER_ID))

bot.run(os.getenv('DISCORD_TOKEN'))