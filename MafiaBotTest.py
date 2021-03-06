__author__ = 'LLCoolDave'

# ToDo: Replace by proper unit tests, currently broken as it stands

import logging
from MafiaBot.MafiaBot import *
from sopel.tools import Identifier

log = logging.getLogger('MafiaBot')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
log.addHandler(ch)
mb = MafiaBot()

mainchannel = mb.mainchannel
deadchat = mb.deadchat
mafiachannel = mb.mafiachannels[0]

playerlist = [Identifier('PLAYERA'), Identifier('PLAYERB'), Identifier('PLAYERC'), Identifier('PLAYERD'), Identifier('PLAYERE'), Identifier('PLAYERF'), Identifier('PLAYERG')]


class botstub:

    def msg(self, target, msg, max_messages=0):
        log.info('BOT MSG @'+str(target)+': '+msg)

    def join(self, param):
        log.info('BOT JOIN: '+param)

    def part(self, param):
        log.info('BOT PART: '+param)

    def write(self, param):
        log.info('BOT WRITE: '+param[0]+param[1])

    def say(self, msg, max_messages=0):
        log.info('BOT SAY: '+msg)

def SendCommand(command, source, nick, param):
    reply = mb.HandleCommand(command, source, nick, param, botstub())
    log.info('COMMAND '+command+' by '+str(nick)+' in '+str(source)+' with parameter \''+str(param)+'\'')
    if reply is not None:
        log.info('RESPONSE ' + reply)

def SendPlayerCommand(command, source, nick, param):
    reply = mb.HandlePlayerCommand(command, source, nick, param, botstub())
    log.info('COMMAND '+command+' by '+str(nick)+' in '+str(source)+' with parameter \''+str(param)+'\'')
    if reply is not None:
        log.info('RESPONSE ' + reply)

def GameLoop():
    mb.GameLoop(botstub())

def LogOff():
    log.setLevel(50)

def LogOn():
    log.setLevel(10)

def JoinAndStart():
    for player in playerlist:
        SendCommand('join', mainchannel, player, '')
    SendCommand('setup', mainchannel, playerlist[0], 'load test')
    SendCommand('setup', mainchannel, playerlist[0], 'daystart')
    SendCommand('players', mainchannel, playerlist[0], '')
    #test votes command
    SendCommand('votes', mainchannel, playerlist[2], '')
    SendCommand('start', mainchannel, playerlist[0], '')
    SendCommand('votes', playerlist[3], playerlist[3], '')


def Vote(player, target='NoLynch'):
    strtar = str(target)
    SendCommand('vote', mainchannel, player, strtar)

def PassDay(target='NoLynch'):
    for player in playerlist:
        Vote(player, target)

def BreakPoint():
    pass

def Main():
    # all players join
    LogOff()
    JoinAndStart()
    # get mafia
    scums = [player for player in playerlist if mb.players[player].faction == MafiaPlayer.FACTION_MAFIA]
    # get prostitute
    prostitutes = [player for player in playerlist if isinstance(mb.players[player].role, Roles['prostitute'])]
    if prostitutes:
        pros = prostitutes[0]
    else:
        pros = None
    # get prostitute
    medics = [player for player in playerlist if isinstance(mb.players[player].role, Roles['medic'])]
    if medics:
        medic = medics[0]
    else:
        medic = None
    cops = [player for player in playerlist if isinstance(mb.players[player].role, Roles['cop'])]
    if cops:
        cop = cops[0]
    else:
        cop = None
    paritycops = [player for player in playerlist if isinstance(mb.players[player].role, Roles['paritycop'])]
    if paritycops:
        paritycop = paritycops[0]
    else:
        paritycop = None
    trackers = [player for player in playerlist if isinstance(mb.players[player].role, Roles['tracker'])]
    if trackers:
        tracker = trackers[0]
    else:
        tracker = None
    watchers = [player for player in playerlist if isinstance(mb.players[player].role, Roles['watcher'])]
    if watchers:
        watcher = watchers[0]
    else:
        watcher = None
    bulletproofs = [player for player in playerlist if isinstance(mb.players[player].role, Roles['bulletproof'])]
    if bulletproofs:
        bulletproof = bulletproofs[0]
    else:
        bulletproof = None
    gunsmiths = [player for player in playerlist if isinstance(mb.players[player].role, Roles['gunsmith'])]
    if gunsmiths:
        gunsmith = gunsmiths[0]
    else:
        gunsmith = None
    vigilantes = [player for player in playerlist if isinstance(mb.players[player].role, Roles['vigilante'])]
    if vigilantes:
        vigilante = vigilantes[0]
    else:
        vigilante = None
    aliens = [player for player in playerlist if isinstance(mb.players[player].role, Roles['alien'])]
    if aliens:
        alien = aliens[0]
    else:
        alien = None
    if scums[0] in prostitutes:
        scum = scums[1]
    else:
        scum = scums[0]
    # get setup
    setup = [(str(player), mb.players[player].GetFaction(), mb.players[player].role.GetRoleName()) for player in playerlist]
    LogOn()
    log.debug('This game\'s setup is: '+str(setup))
    i = 0
    while mb.active:
        # lynch player i
        PassDay(playerlist[i])
        LogOff()
        SendPlayerCommand('pass', gunsmith, gunsmith, bulletproof)
        SendPlayerCommand('pass', pros, pros, cop)
        SendPlayerCommand('pass', medic, medic, playerlist[0])
        SendPlayerCommand('pass', cop, cop, playerlist[0])
        SendPlayerCommand('pass', tracker, tracker, cop)
        SendPlayerCommand('pass', watcher, watcher, cop)
        SendPlayerCommand('pass', vigilante, vigilante, cop)
        SendPlayerCommand('check', paritycop, paritycop, playerlist[6-i])
        SendCommand('nokill', mafiachannel, scum, playerlist[0])
        SendCommand('nokill', mafiachannel, pros, playerlist[0])
        LogOn()
        GameLoop()
        i += 1





if __name__ == "__main__":
    Main()
