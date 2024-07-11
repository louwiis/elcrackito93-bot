import discord
from discord.ext import tasks
from discord import app_commands
from discord import ButtonStyle, ui, Message, Interaction

import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.append('boosts')
from utils import search_boosts


intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
SERVER_ID = os.getenv('SERVER_ID')


# @tree.command(
#     name="ping",
#     description="My first application Command",
#     guild=discord.Object(id=SERVER_ID)
# )
# async def first_command(interaction):
#     await interaction.response.send_message("Pong!", ephemeral=True)

# every 10 seconds
@tasks.loop(seconds=15)
async def boosts():
    await search_boosts(bot)

@bot.event
async def on_ready():
    # await tree.sync(guild=discord.Object(id=SERVER_ID))
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    boosts.start()

bot.run(os.getenv('DISCORD_TOKEN'))