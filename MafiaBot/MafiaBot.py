__author__ = 'LLCoolDave'

import random
from MafiaPlayer import MafiaPlayer
from sopel.tools import Identifier

class MafiaBot:

    DAWN = 0
    DAYPHASE = 1
    DUSK = 2
    NIGHTPHASE = 3

    NOVOTE = ''


    def __init__(self):
        self.deadchat = ''
        self.mafiachannels = []
        self.players = dict()
        self.mainchannel = '#mafiabotdebug'
        self.joinchannels = False
        self.active = False
        self.phase = self.DAYPHASE
        self.votes = dict()
        self.actionlist = list()
        self.daycount = 1

        self.ResetGame()

    def __getitem__(self, item):
        try:
           return self.players[item]
        except:
            return None

    def __setitem__(self, key, value):
        self.players[key] = value

    def ResetGame(self):
        self.deadchat = '#deadchat'+str(random.randrange(10000))
        self.mafiachannels = ['#mafiadebug']  # ['#mafia'+str(random.randrange(10000))]
        self.players = dict()
        self.joinchannels = True
        self.active = False
        self.phase = self.DAYPHASE
        self.votes = dict()
        self.actionlist = list()
        self.daycount = 1

    def HandlePlayerCommand(self, command, source, nick, param, bot):
        if nick in self.players:
            if not self.players[nick].IsDead():
                return self.players[nick].HandleCommand(command, param, bot, self)
        return None

    def HandleCommand(self, command, source, nick, param, bot):
        if command == 'abort':
            # leave active channels
            for chn in self.mafiachannels:
                bot.part(chn)
            bot.part(self.deadchat)
            self.ResetGame()
            # rejoin new channels and set silent mode for mafia channels
            for chn in self.mafiachannels:
                bot.join(chn)
                bot.write(('MODE ', chn+' +s'))
            bot.join(self.deadchat)
            return None

        elif command == 'deadchat':
            return "The deadchat is at "+self.deadchat

        elif command == 'join':
            if not self.active and nick not in self.players:
                self[nick] = MafiaPlayer()
                bot.msg(self.mainchannel, nick + ' has joined the game. There are currently '+str(len(self.players))+' Players in the game.')
            return None

        elif command == 'start':
            self.StartGame(bot)
            return None

        elif command == 'vote':
            if self.active and self.phase == self.DAYPHASE and nick in self.players:
                self.HandleVote(nick, param, bot)
                return None
            else:
                return None

        elif command == 'unvote':
            if self.active and nick in self.players:
                self.votes[nick] = self.NOVOTE
                self.PrintVotes(bot)
                return None
            else:
                return None

        elif command == 'votes':
            self.PrintVotes(bot)
            return None

        elif command == 'players':
            if not self.players:
                return 'No players active'
            else:
                msg = 'Playerlist: ' + self.GetPlayers()
                return msg

        # template
        elif command == '':
            return None

        return "I do not currently know how to handle command "+command

    def GetPlayers(self):
        msg = ''
        for player in self.players.keys():
            if self.active:
                #if game is going only add alive players
                if not self.players[player].IsDead():
                    msg += player + ', '
            else:
                msg += player + ', '
        return msg[:-2]

    def GetChannels(self):
        return list(self.mafiachannels).append(self.deadchat)

    def IsDead(self, player):
        try:
            return self[player].IsDead()
        except:
            return True

    def MayJoin(self, player, channel):
        if player in self.players:
            if self[player].mafiachannel == channel:
                return True
            else:
                return False
        else:
            return False

    def HandleVote(self, player, param, bot):
        if not self[player].IsDead():
            if Identifier(param) in self.players or param == 'NoLynch':
                self.votes[player] = param
                # check for majority
                cnt = 0
                for vote in self.votes.values():
                    if vote == param:
                        cnt += 1
                if cnt > len(self.votes)/2 :
                    #majority
                    self.Lynch(Identifier(param), bot)
                else:
                    # print current votes
                    self.PrintVotes(bot)

    def PrintVotes(self, bot):
        msg = 'Current Votes -  '
        for pair in self.votes.items():
            if pair[1] == self.NOVOTE:
                msg += pair[0] + ': No Vote '
            else:
                msg += pair[0] + ': ' + pair[1] + ' '
        msg += ' - ' + str(len(self.votes)/2 + 1) + ' votes required for a lynch.'
        bot.msg(self.mainchannel, msg, max_messages=10)

    def Lynch(self, player, bot):
        if player == 'NoLynch':
            bot.msg(self.mainchannel, 'The town decides not to lynch anybody today.', max_messages=10)
        else:
            rolename = self.players[player].Kill(self)
            bot.msg(self.mainchannel, player+', the '+rolename+' was lynched today!', max_messages=10)
        if not self.CheckForWinCondition(bot):
            self.BeginNightPhase(bot)

    def CheckForWinCondition(self, bot):
        # just for testing: check if anybody is alive
        alldead = True
        for player in self.players:
            if not self.players[player].IsDead():
                alldead = False
                break
        if alldead:
            self.active = False
            bot.msg(self.mainchannel, 'The game has ended!')

        return alldead

    def StartGame(self, bot):
        self.active = True
        self.votes = dict()
        for player in self.players.keys():
            self[player].dead = False
            self.votes[player] = self.NOVOTE
            # send role PM to all of the players
            bot.msg(player, self[player].GetRolePM())
        bot.msg(self.mainchannel, 'The game has started!')

    def HandleActionList(self, bot):
        pass

    def BeginNightPhase(self, bot):
        # ToDo set action required flags for players
        self.phase = self.NIGHTPHASE
        bot.msg(self.mainchannel, 'Night '+str(self.daycount)+' has started. Go to sleep and take required actions.')

    # called every 2 seconds
    def GameLoop(self, bot):
        if self.joinchannels:
            for chn in self.mafiachannels:
                bot.join(chn)
                bot.write(('MODE ', chn+' +s'))
            bot.join(self.deadchat)
            bot.join(self.mainchannel)
            self.joinchannels = False

        if self.active and self.phase == self.NIGHTPHASE:
            # handle nightphase
            # check if there are more actions required to be taken
            requiredactions = False
            for player in self.players:
                if not self.players[player].IsDead():
                    if self.players[player].requiredAction == True:
                        requiredactions = True
            if not requiredactions:
                self.HandleActionList(bot)
                if not self.CheckForWinCondition(bot):
                    self.daycount += 1
                    self.phase = self.DAYPHASE
                    bot.msg(self.mainchannel, 'Day '+str(self.daycount)+' has just begun. The Town consists of '+self.GetPlayers())

