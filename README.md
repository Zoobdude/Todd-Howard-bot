# Todd Bot

## What is this?

A very simple dicord bot I was requested to make for a friend.

It randomly re-posts people's messages putting quotation marks around a random word in the message.


## Commands

* `/set_freq {freq}` Used to set the frequency of the bot's replies. Freq should be a float between 0 and 1. One meaning it will reply always, and zero meaning it will never.

* `/disable` Used to disable the bot in a specific channel

* `/enable` Used to re-enable the bot in a specific channel


## Usage

### [Invite my instance](https://discord.com/oauth2/authorize?client_id=1211749407582588968&permissions=2048&scope=bot)

or

### Run the bot yourself

##### Generate a token

[Go to the discord for developers website](https://discord.com/developers)

Required permissions
* MESSAGE CONTENT INTENT
* Send Messgaes


##### Docker command:
```
sudo docker run \
-e DISCORD_TOKEN="INSERT_DICORD_TOKEN_HERE"  \
--volume $(pwd)/Todd-bot:/data \
--detach \
--restart unless-stopped \
--name Todd \
zoobdude/todd-howard-bot
```