# ToDo: Replace by proper unit tests, currently broken as it stands

import logging
from ResistanceBot.ResistanceBot import *
from sopel.tools import Identifier

log = logging.getLogger('ResistanceBot')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
log.addHandler(ch)
rb = ResistanceBot()

channel = rb.channel

playerlist = [Identifier('PLAYERA'), Identifier('PLAYERB'), Identifier('PLAYERC'), Identifier('PLAYERD'), Identifier('PLAYERE'), Identifier('PLAYERF'), Identifier('PLAYERG'), Identifier('PLAYERH')]


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
    reply = rb.HandleCommand(command, source, nick, param, botstub())
    log.info('COMMAND '+command+' by '+str(nick)+' in '+str(source)+' with parameter \''+str(param)+'\'')
    if reply is not None:
        log.info('RESPONSE ' + reply)


def LogOff():
    log.setLevel(50)


def LogOn():
    log.setLevel(10)


def JoinAndStart():
    for player in playerlist:
        SendCommand('join', channel, player, '')
    SendCommand('start', channel, playerlist[0], '')


def BreakPoint():
    pass


def Main():
    # all players join
    LogOff()
    JoinAndStart()
    # get mafia
    spies = [player for player in playerlist if rb.players[player].faction == ResistancePlayer.FACTION_SPIES]
    resistance = list(set(playerlist).difference(set(spies)))
    # get setup
    log.info('Spies: '+str(spies))
    log.info('Resistance: '+str(resistance))
    LogOn()
    while rb.active:
        leader = rb.leader
        missioncount = rb.mission_required
        mission = random.sample(playerlist, missioncount)
        for player in mission:
            SendCommand('team', channel, leader, player)
        # vote on team
        for player in playerlist:
            if random.random() < 0.4:
                yesno = 'yes'
            else:
                yesno = 'no'
            SendCommand('teamvote', player, player, yesno)
        # check if vote passed, then carry out mission
        if rb.phase == rb.MISSIONPHASE:
            for player in mission:
                if player in spies:
                    if random.random() < 0.4:
                        yesno = 'success'
                    else:
                        yesno = 'fail'
                else:
                    yesno = 'success'
                SendCommand('missionvote', player, player, yesno)

if __name__ == "__main__":
    Main()
