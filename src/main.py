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

#--------------------------------------------------------------------------------
#DB updates

#--------------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f'Sucsessfully logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you and mocking you"))

@bot.event
async def on_guild_join(guild):
    print(f"Joined {guild.name} with {guild.member_count} members")
    config_db.insert({"guild_id": guild.id, "frequency": 0.1, "disabled_channels": [], "specific_channel_frequency": {}})

@bot.event
async def on_guild_remove(guild):
    print(f"Left {guild.name} with {guild.member_count} members")
    config_db.remove(where("guild_id") == guild.id)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        # Bot's own message therefore do nothing
        return

    if message.channel.id in config_db.get(where("guild_id") == message.guild.id)["disabled_channels"]:
        # Bot is disabled in this channel
        return
    
    if str(message.channel.id) in config_db.get(where("guild_id") == message.guild.id)["specific_channel_frequency"]:
        frequency_bias = config_db.get(where("guild_id") == message.guild.id)["specific_channel_frequency"][str(message.channel.id)]

    else:
        frequency_bias = config_db.get(where("guild_id") == message.guild.id)["frequency"]

    
    if not true_false_random(frequency_bias):
        # Decided not to respond
        return

    response = put_quotes_around_random_word(message.content)
    
    await message.channel.send(response)
        

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


@bot.command(description="Set the global frequency of the bot's responses")
async def set_global_frequency(ctx, freq: float):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You do not have permission to do that!")
        return
    
    if freq < 0 or freq > 1:
        await ctx.respond("Frequency must be between 0 and 1", ephemeral=True)
        return

    config_db.update({"frequency": freq}, where("guild_id") == ctx.guild.id)
    await ctx.respond(f"Set the frequency to {freq}", ephemeral=True)

@bot.command(description="Set the frequency of the bot's responses in a specific channel (-1 to set back to server default)")
async def set_channel_frequency(ctx, freq: float):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You do not have permission to do that!")
        return
    
    channel_frequency = config_db.get(where("guild_id") == ctx.guild.id)["specific_channel_frequency"]
    
    if freq == -1:
        if str(ctx.channel.id) in channel_frequency:
            channel_frequency.pop(str(ctx.channel.id))
            config_db.update({"specific_channel_frequency": channel_frequency}, where("guild_id") == ctx.guild.id)
            await ctx.respond(f"Set the frequency to server default", ephemeral=True)
            return
        
        else:
            await ctx.respond("The frequency is already set to server default", ephemeral=True)
            return
    
    if freq < 0 or freq > 1:
        await ctx.respond("Frequency must be between 0 and 1", ephemeral=True)
        return

    channel_frequency[str(ctx.channel.id)] = freq
    config_db.update({"specific_channel_frequency": channel_frequency}, where("guild_id") == ctx.guild.id)
    await ctx.respond(f"Set the frequency to {freq}", ephemeral=True)

    
bot.run(TOKEN)