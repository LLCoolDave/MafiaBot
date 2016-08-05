import discord
from MafiaBot.MafiaBot import MafiaBot
from MafiaBot.DiscordCommunication import DiscordCommunication
import io
import os

client = discord.Client()
mb = None

approved_channels = ['gamechat', 'deadchat', 'mafia']


@client.event
async def on_ready():
    global mb
    mb = MafiaBot(DiscordCommunication(client))
    await mb.communication.process_queue()
    print('Connected to Discord')


@client.event
async def on_message(message):
    # filter out messages that are from channels the bot is not supposed to partake in
    if not message.channel.is_private and message.channel.name not in approved_channels:
        return

    if mb is not None:
        something_happend = False
        if message.content.startswith('!'):
            # split message
            splits = message.content[1:].split(' ', 1)
            command = splits[0]
            params = splits[1] if len(splits) > 1 else ''

            # help
            if command == 'help':
                await client.send_message(message.channel, 'https://docs.google.com/document/d/1XhWJLpKSxM8BcRaTB980OPBcAAMBQfIrR15SmM6f7Ro')

            # channel messages
            elif command in ['start', 'team', 'playerorder', 'order', 'kill', 'nokill', 'vote', 'unvote', 'nolynch'] and not message.channel.is_private:
                mb.HandleCommand(command, message.channel, message.author.name, params)
                something_happend = True

            # private messages
            elif command in ['shoot', 'check', 'protect', 'block', 'use', 'pass', 'visit', 'track', 'watch', 'pick', 'items', 'send', 'probes', 'afk', 'back', 'teamvote', 'missionvote'] and message.channel.is_private:
                mb.HandlePlayerCommand(command, message.author.name, params)
                something_happend = True

            # generic commands that work either way
            elif command in ['role', 'roles', 'deadchat', 'votes', 'players', 'join', 'setup', 'phase', 'drop', 'time', 'item', 'dice', 'abort']:
                mb.HandleCommand(command, message.channel, message.author.name, params)
                something_happend = True

        if something_happend:
            mb.GameLoop()
            await mb.communication.process_queue()

with io.open(os.path.join(os.path.dirname(__file__), 'token'), 'r') as tokenfile:
    token = tokenfile.read()
client.run(token)
