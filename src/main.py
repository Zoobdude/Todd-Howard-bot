import random
import os

from logic import put_quotes_around_random_word, true_false_random

import discord
from tinydb import TinyDB, where

TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    print("Discord bot token not found")
    exit()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = discord.Bot(intents=intents)

config_db = TinyDB("data/ToddBotConfig.json")

@bot.event
async def on_ready():
    print(f'Sucsessfully logged in as {bot.user}')

@bot.event
async def on_guild_join(guild):
    print(f"Joined {guild.name} with {guild.member_count} members")
    config_db.insert({"guild_id": guild.id, "frequency": 0.1, "disabled_channels": []})

@bot.event
async def on_guild_remove(guild):
    print(f"Left {guild.name} with {guild.member_count} members")
    config_db.remove(where("guild_id") == guild.id)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        # Bot's own message therefore do nothing
        return

    if message.channel.id in config_db.search(where("guild_id") == message.guild.id)[0]["disabled_channels"]:
        # Bot is disabled in this channel
        return
    
    frequency_bias = config_db.search(where("guild_id") == message.guild.id)[0]["frequency"]
    
    if not true_false_random(frequency_bias):
        # Decided not to respond
        return

    response = put_quotes_around_random_word(message.content)
    
    await message.channel.send(response)
        

#Disable in specific channel slash command
@bot.command(description="Disable the bot in a specific channel")
async def disable(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You do not have permission to do that!")
        return
    
    if ctx.channel.id in config_db.search(where("guild_id") == ctx.guild.id)[0]["disabled_channels"]:
        await ctx.respond("The bot is already disabled in this channel")
        return

    current_disabled_channels = config_db.search(where("guild_id") == ctx.guild.id)[0]["disabled_channels"]
    current_disabled_channels.append(ctx.channel.id)
    config_db.update({"disabled_channels": current_disabled_channels}, where("guild_id") == ctx.guild.id)
        
    print(f"Disabled the bot in {ctx.channel.name}")
    
    await ctx.respond(f"Disabled the bot in {ctx.channel.name}", ephemeral=True)

        
        
@bot.command(description="Enable the bot in a specific channel")
async def enable(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You do not have permission to do that!")
        return
    
    if ctx.channel.id not in config_db.search(where("guild_id") == ctx.guild.id)[0]["disabled_channels"]:
        await ctx.respond("The bot is already enabled in this channel")
        return
    
    current_disabled_channels = config_db.search(where("guild_id") == ctx.guild.id)[0]["disabled_channels"]
    current_disabled_channels.remove(ctx.channel.id)
    config_db.update({"disabled_channels": current_disabled_channels}, where("guild_id") == ctx.guild.id)
    
    await ctx.respond(f"Enabled the bot in {ctx.channel.name}", ephemeral=True)


@bot.command(description="Set the frequency of the bot's responses")
async def set_frequency(ctx, freq: float):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You do not have permission to do that!")
        return
    
    if freq < 0 or freq > 1:
        await ctx.respond("Frequency must be between 0 and 1", ephemeral=True)
        return

    config_db.update({"frequency": freq}, where("guild_id") == ctx.guild.id)
    await ctx.respond(f"Set the frequency to {freq}", ephemeral=True)

    
bot.run(TOKEN)