from sopel import module
import MafiaBot.MafiaBot

# ToDo: Modify bot.msg to reduce wait time, otherwise things are way too slow and blocked due to the threadlock on mb

def setup(bot):
    mb = MafiaBot.MafiaBot.MafiaBot()
    bot.memory['MafiaBotDir'] = mb


@module.event('JOIN')
@module.rule(r'.*')
def JoinHandler(bot, trigger):
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
    channels = bot.memory['MafiaBotDir'].GetChannels()
    if channels is not None:
        for chn in channels:
            if not chn == '#fridaynightmafia':
                bot.part(chn)
    reload(MafiaBot.MafiaBot)
    mb = MafiaBot.MafiaBot.MafiaBot()
    bot.memory['MafiaBotDir'] = mb
    for chn in mb.mafiachannels:
        bot.join(chn)
        bot.write(('MODE ', chn+' +s'))
    bot.join(mb.deadchat)


@module.commands('start', 'kill', 'nokill', 'vote', 'unvote', 'nolynch')
@module.require_chanmsg()
def ChannelOnly(bot, trigger):
    response = bot.memory['MafiaBotDir'].HandleCommand(trigger.group(1), trigger.sender, trigger.nick, trigger.group(2), bot)
    if response is not None:
        bot.say(response, max_messages=10)


@module.commands('abort')
@module.require_admin()
def AdminOnly(bot, trigger):
    response = bot.memory['MafiaBotDir'].HandleCommand(trigger.group(1), trigger.sender, trigger.nick, trigger.group(2), bot)
    if response is not None:
        if trigger.is_privmsg:
            bot.msg(trigger.nick, response, max_messages=10)
        else:
            bot.say(response, max_messages=10)


@module.commands('shoot', 'check', 'protect', 'block', 'use', 'pass', 'visit')
@module.require_privmsg()
def PlayerAction(bot, trigger):
    response = bot.memory['MafiaBotDir'].HandlePlayerCommand(trigger.group(1), trigger.sender, trigger.nick, trigger.group(2), bot)
    if response is not None:
        bot.msg(trigger.nick, response, max_messages=10)


@module.commands('role', 'roles', 'deadchat', 'votes', 'players', 'join', 'setup', 'setsetup', 'phase')
def Generic(bot, trigger):
    response = bot.memory['MafiaBotDir'].HandleCommand(trigger.group(1), trigger.sender, trigger.nick, trigger.group(2), bot)
    if response is not None:
        if trigger.is_privmsg:
            bot.msg(trigger.nick, response, max_messages=10)
        else:
            bot.say(response, max_messages=10)


@module.interval(5)
def GameLoop(bot):
    # main game loop, check for states and handle them as necessary
    bot.memory['MafiaBotDir'].GameLoop(bot)