import random
import os

from rando_quote import put_quotes_around_random_word

import discord

TOKEN = os.getenv("DISCORD TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'Sucsessfully logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        # Bot's own message therefore do nothing
        return

    response = put_quotes_around_random_word(message.content)
    print(response)
    
    await message.channel.send(response)
        

'''
@bot.slash_command(name="Disable in this channel", description="Disables the bot in the current channel",)
aysnc def disable_in_channel(ctx):
'''


bot.run('your token here')