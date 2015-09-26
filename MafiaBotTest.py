__author__ = 'LLCoolDave'

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

playerlist = [Identifier('PLAYERA'), Identifier('PLAYERB'), Identifier('PLAYERC'), Identifier('PLAYERD'), Identifier('PLAYERE'), Identifier('PLAYERF')]


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
    log.info('COMMAND '+command+' by '+str(nick)+' in '+str(source)+' with parameter \''+param+'\'')
    if reply is not None:
        log.info('RESPONSE ' + reply)

def SendPlayerCommand(command, source, nick, param):
    reply = mb.HandlePlayerCommand(command, source, nick, param, botstub())

def GameLoop():
    mb.GameLoop(botstub())

def LogOff():
    log.setLevel(50)

def LogOn():
    log.setLevel(10)

def JoinAndStart():
    for player in playerlist:
        SendCommand('join', mainchannel, player, '')
    SendCommand('players', mainchannel, playerlist[0], '')
    #test votes command
    SendCommand('votes', mainchannel, playerlist[2], '')
    SendCommand('start', mainchannel, playerlist[0], '')
    SendCommand('votes', playerlist[3], playerlist[3], '')


def Vote(player, target='NoLynch'):
    strtar = str(target)
    SendCommand('vote', mainchannel, player, strtar)

def PassDay():
    for player in playerlist:
        Vote(player)

def BreakPoint():
    pass

def Main():
    LogOff()
    # all players join
    JoinAndStart()
    LogOn()
    #get mafia players
    scum = [player for player in playerlist if mb.players[player].faction == MafiaPlayer.FACTION_MAFIA]
    log.debug('Mafia this game are: '+str(scum))
    # go to night
    LogOff()
    PassDay()
    LogOn()
    SendCommand('phase', mainchannel, playerlist[4], '')
    # test kill command
    log.info('No reply expected: ')
    SendCommand('kill', mainchannel, scum[0], playerlist[0])
    log.info('Positive reply expected: ')
    SendCommand('kill', mafiachannel, scum[0], playerlist[0])
    log.info('Negative response expected: ')
    SendCommand('kill', mafiachannel, scum[1], playerlist[0])
    GameLoop()
    SendCommand('phase', mainchannel, playerlist[4], '')
    BreakPoint()




if __name__ == "__main__":
    Main()
