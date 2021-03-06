from sopel import module
from MafiaBot.MafiaBot import MafiaBot
from MafiaBot.SopelCommunication import SopelCommunication
import ResistanceBot.ResistanceBot

# ToDo: Modify bot.msg to reduce wait time, otherwise things are way too slow and blocked due to the threadlock on mb


def setup(bot):
    mb = MafiaBot(SopelCommunication(bot))
    bot.memory['MafiaBotDir'] = mb
    rb = ResistanceBot.ResistanceBot.ResistanceBot()
    bot.memory['ResistanceBot'] = rb
    bot.memory['mode'] = 'mafia'


@module.event('JOIN')
@module.rule(r'.*')
def JoinHandler(bot, trigger):
    if bot.memory['mode'] == 'mafia':
        if not trigger.nick == bot.nick:
            mb = bot.memory['MafiaBotDir']
            if trigger.sender == mb.deadchat:
                # check if player is allowed to join
                if not mb.IsDead(trigger.nick):
                    bot.write(('KICK ', trigger.sender+' '+trigger.nick))
            elif trigger.sender in mb.mafiachannels:
                if not mb.MayJoin(trigger.nick, trigger.sender):
                    bot.write(('KICK ', trigger.sender+' '+trigger.nick))


@module.commands('reset')
@module.require_owner()
def Reset(bot, trigger):
    if bot.memory['mode'] == 'mafia':
        channels = bot.memory['MafiaBotDir'].GetChannels()
        if channels is not None:
            for chn in channels:
                if not chn == '#fridaynightmafia':
                    bot.part(chn)
        mb = MafiaBot(SopelCommunication(bot))
        bot.memory['MafiaBotDir'] = mb
        for chn in mb.mafiachannels:
            bot.join(chn)
            bot.write(('MODE ', chn+' +s'))
        bot.join(mb.deadchat)


@module.commands('start', 'team', 'playerorder', 'order', 'kill', 'nokill', 'vote', 'unvote', 'nolynch')
@module.require_chanmsg()
def ChannelOnly(bot, trigger):
    response = None
    if bot.memory['mode'] == 'mafia':
        bot.memory['MafiaBotDir'].HandleCommand(trigger.group(1), trigger.sender, trigger.nick, trigger.group(2))
    elif bot.memory['mode'] == 'resistance':
        response = bot.memory['ResistanceBot'].HandleCommand(trigger.group(1), trigger.sender, trigger.nick, trigger.group(2), bot)
    if response is not None:
        bot.say(response, max_messages=10)


@module.commands('mafia')
@module.require_chanmsg()
def MafiaCommand(bot, trigger):
    bot.memory['mode'] = 'mafia'
    bot.say('Bot switched to Mafia mode.')


@module.commands('resistance')
@module.require_chanmsg()
def MafiaCommand(bot, trigger):
    bot.memory['mode'] = 'resistance'
    bot.say('Bot switched to Resistance mode.')


@module.commands('help')
def Help(bot, trigger):
    if bot.memory['mode'] == 'mafia':
        bot.say('https://docs.google.com/document/d/1XhWJLpKSxM8BcRaTB980OPBcAAMBQfIrR15SmM6f7Ro', max_messages=10)


@module.commands('abort')
@module.require_admin()
def AdminOnly(bot, trigger):
    response = None
    if bot.memory['mode'] == 'mafia':
        bot.memory['MafiaBotDir'].HandleCommand(trigger.group(1), trigger.sender, trigger.nick, trigger.group(2))
    elif bot.memory['mode'] == 'resistance':
        response = bot.memory['ResistanceBot'].HandleCommand(trigger.group(1), trigger.sender, trigger.nick, trigger.group(2), bot)
    if response is not None:
        if trigger.is_privmsg:
            bot.msg(trigger.nick, response, max_messages=10)
        else:
            bot.say(response, max_messages=10)


@module.commands('shoot', 'check', 'protect', 'block', 'use', 'pass', 'visit', 'track', 'watch', 'pick', 'items', 'send', 'probes', 'afk', 'back', 'teamvote', 'missionvote')
@module.require_privmsg()
def PlayerAction(bot, trigger):
    response = None
    if bot.memory['mode'] == 'mafia':
        bot.memory['MafiaBotDir'].HandlePlayerCommand(trigger.group(1), trigger.nick, trigger.group(2))
    elif bot.memory['mode'] == 'resistance':
        response = bot.memory['ResistanceBot'].HandleCommand(trigger.group(1), trigger.sender, trigger.nick, trigger.group(2), bot)
    if response is not None:
        bot.msg(trigger.nick, response, max_messages=10)


@module.commands('role', 'roles', 'deadchat', 'votes', 'players', 'join', 'setup', 'phase', 'drop', 'time', 'item', 'dice')
def Generic(bot, trigger):
    response = None
    if bot.memory['mode'] == 'mafia':
        bot.memory['MafiaBotDir'].HandleCommand(trigger.group(1), trigger.sender, trigger.nick, trigger.group(2))
    elif bot.memory['mode'] == 'resistance':
        response = bot.memory['ResistanceBot'].HandleCommand(trigger.group(1), trigger.sender, trigger.nick, trigger.group(2), bot)
    if response is not None:
        if trigger.is_privmsg:
            bot.msg(trigger.nick, response, max_messages=10)
        else:
            bot.say(response, max_messages=10)


@module.interval(1)
def GameLoop(bot):
    if bot.memory['mode'] == 'mafia':
        # main game loop, check for states and handle them as necessary
        bot.memory['MafiaBotDir'].GameLoop(bot)
