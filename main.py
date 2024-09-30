import discord
from discord.ext import tasks
from discord import app_commands
from discord import ButtonStyle, ui, Message, Interaction

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
    description="Calculate la value et la mise à jouer de la trueodds et de la cote prise",
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
    description="Calculate la value et la mise à jouer de la trueodds et de la cote prise",
    guild=discord.Object(id=MT_SERVER_ID)
)
async def public_value(interaction, trueodds: float, taken_odds: float):
    value = (taken_odds - trueodds) / trueodds * 100 
    kelly = value / (taken_odds - 1)


    # make a message to show the percentage value and the 4 types of kelly
    # make an embed it will be easier

    embed = discord.Embed(
        title=f"Calcul de value et de mise",
        description=f"Trueodds: {trueodds}\nCote prise: {taken_odds}\nValue: {value:.2f}%",
        color=0xFFFFFF
    )

    embed.add_field(name="Kelly/2", value=f"{kelly/2:.2f}%", inline=True)
    embed.add_field(name="Kelly/3", value=f"{kelly/3:.2f}%", inline=True)
    embed.add_field(name="Kelly/4", value=f"{kelly/4:.2f}%", inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=False)    

@bot.event
async def on_ready():
    # await tree.sync(guild=discord.Object(id=SERVER_ID))
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    # boosts.start()

    await tree.sync(guild=discord.Object(id=MT_SERVER_ID))

bot.run(os.getenv('DISCORD_TOKEN'))