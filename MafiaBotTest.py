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

class botstub:

    def msg(self, target, msg, max_messages=0):
        log.info('BOT MSG @'+str(target)+': '+msg)

    def join(self, param):
        log.info('BOT JOIN: '+param)

    def part(self, param):
        log.info('BOT PART: '+param)

    def write(self, param1, param2):
        log.info('BOT WRITE: '+param1+param2)

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

def Main():
    mainchannel = mb.mainchannel
    deadchat = mb.deadchat
    mafiachannel = mb.mafiachannels[0]

    playerlist = [Identifier('PLAYERA'), Identifier('PLAYERB'), Identifier('PLAYERC'), Identifier('PLAYERD'), Identifier('PLAYERE')]
    # all players join
    SendCommand('join', mainchannel, playerlist[0], '')
    SendCommand('join', mainchannel, playerlist[1], '')
    SendCommand('join', mainchannel, playerlist[2], '')
    SendCommand('join', mainchannel, playerlist[3], '')
    SendCommand('join', mainchannel, playerlist[4], '')
    SendCommand('players', mainchannel, playerlist[0], '')
    #test votes command
    SendCommand('votes', mainchannel, playerlist[2], '')
    SendCommand('start', mainchannel, playerlist[0], '')
    SendCommand('votes', playerlist[3], playerlist[3], '')

if __name__ == "__main__":
    Main()
