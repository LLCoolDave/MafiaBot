__author__ = 'LLCoolDave'

import random
from MafiaPlayer import MafiaPlayer
from sopel.tools import Identifier
from MafiaAction import MafiaAction
from MafiaRole import MafiaRole
from Roles.rolelist import Roles

class MafiaBot:

    DAWN = 0
    DAYPHASE = 1
    DUSK = 2
    NIGHTPHASE = 3

    PhaseStr = {0: 'Dawn', 1: 'Day', 2: 'Dusk', 3: 'Night'}

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
        self.revealrolesondeath = True
        self.revealfactionondeath = True
        self.factionkills = 0

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
        self.revealrolesondeath = True
        self.revealfactionondeath = True
        self.factionkills = 0

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
                bot.write(('MODE ', chn+' +s', dict()))
            bot.join(self.deadchat)
            return None

        elif command == 'deadchat':
            return "The deadchat is at "+self.deadchat

        elif command == 'join':
            if not self.active and nick not in self.players:
                self[nick] = MafiaPlayer(nick)
                bot.msg(self.mainchannel, nick + ' has joined the game. There are currently '+str(len(self.players))+' Players in the game.', dict())
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

        elif command == 'nolynch':
            if self.active and self.phase == self.DAYPHASE and nick in self.players:
                self.HandleVote(nick, 'NoLynch', bot)
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
            if self.active and self.phase == self.DAYPHASE:
                self.PrintVotes(bot)
            return None

        elif command == 'players':
            if not self.players:
                return 'No players active'
            else:
                msg = 'Playerlist: ' + self.GetPlayers()
                return msg

        elif command == 'kill':
            # check if message came from a mafia channel
            if str(source) in self.mafiachannels:
                # check if it is night
                if self.phase == self.NIGHTPHASE:
                    # check if player is alive and mafia
                    if not self.players[nick].IsDead() and self.players[nick].faction == MafiaPlayer.FACTION_MAFIA:
                        # check if there are kills left
                        if self.factionkills <= 0:
                            return 'There are no faction kills left to be carried out tonight.'
                        else:
                            # check if player exists, is alive
                            identparam = Identifier(param)
                            if identparam in self.players:
                                if not self.players[identparam].IsDead():
                                    # player can be killed, so we add the action
                                    self.actionlist.append(MafiaAction(MafiaAction.KILL, nick, identparam, True))
                                    self.factionkills -= 1
                                    return nick+' will kill '+identparam+' tonight.'

                            # couldn't find valid kill target
                            return param + ' is not a player that can be killed!'
            return None

        elif command == 'nokill':
            # check if message came from a mafia channel
            if str(source) in self.mafiachannels:
                # check if it is night
                if self.phase == self.NIGHTPHASE:
                    # check if player is alive and mafia
                    if not self.players[nick].IsDead() and self.players[nick].faction == MafiaPlayer.FACTION_MAFIA:
                        # check if there are kills left
                        if self.factionkills <= 0:
                            return 'There are no faction kills left to be carried out tonight.'
                        else:
                            # pass remaining kills
                            self.factionkills = 0
                            return 'You forgo any outstanding faction kills for the night.'
            return None

        elif command == 'phase':
            if self.active:
                return 'It is currently '+self.PhaseStr[self.phase]+' on Day '+str(self.daycount)
            return None

        elif command == 'role':
            if param.lower() in Roles:
                return Roles[param.lower()].GetRoleDescription()
            else:
                return 'I do not know the role '+param

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
            killok, playerflip = self.players[player].Kill(self, bot, False)
            if killok:
                bot.msg(self.mainchannel, player+playerflip+' was lynched today!', max_messages=10)
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
            bot.msg(self.mainchannel, 'The game has ended!', dict())

        return alldead

    def StartGame(self, bot):
        self.active = True
        self.votes = dict()
        self.AssignRoles()
        for player in self.players.keys():
            self[player].dead = False
            self.votes[player] = self.NOVOTE
            # send role PM to all of the players
            bot.msg(player, self[player].GetRolePM())
        bot.msg(self.mainchannel, 'The game has started! It is now Day 1.', dict())

    def AssignRoles(self):
        # ToDo Proper handling of this
        # for now, we use a simple system to assign goons and Townies
        playercount = len(self.players)
        mafiacount = (playercount / 5) + 1  # 20% mafia for the start
        if playercount == 7:
            # use the basic setup
            mafiacount = 2
            rolelist = [(MafiaPlayer.FACTION_MAFIA, 'goon', dict()),
                        (MafiaPlayer.FACTION_MAFIA, 'prostitute', {'limiteduses': 1}),
                        (MafiaPlayer.FACTION_TOWN, 'cop', dict()),
                        (MafiaPlayer.FACTION_TOWN, 'medic', dict()),
                        (MafiaPlayer.FACTION_TOWN, 'civilian', dict()),
                        (MafiaPlayer.FACTION_TOWN, 'civilian', dict()),
                        (MafiaPlayer.FACTION_TOWN, 'civilian', dict())]
        else:
            rolelist = [(MafiaPlayer.FACTION_MAFIA, 'goon', dict())]*mafiacount + [(MafiaPlayer.FACTION_TOWN, 'civilian', dict())]*(playercount-mafiacount)
        random.shuffle(rolelist)
        # assign roles to players
        i = 0
        for player in self.players.values():
            # set faction
            player.faction = rolelist[i][0]
            if player.faction == MafiaPlayer.FACTION_MAFIA:
                player.mafiachannel = self.mafiachannels[0]
            # instantiate role
            if rolelist[i][1] is not None:
                # create role
                if rolelist[i][1] in Roles:
                    player.role = Roles[rolelist[i][1]](rolelist[i][2])
                else:
                    #create dummy role
                    player.role = MafiaRole()
            i += 1

    def HandleActionList(self, bot):
        # handle roleblocks
        blockset = set([action.target for action in self.actionlist if action.actiontype == MafiaAction.BLOCK])
        # handle kill actions
        killlist = [action for action in self.actionlist if action.actiontype == MafiaAction.KILL and action.source not in blockset]
        for kill in killlist:
            killstatus, flipmsg = self.players[kill.target].Kill(self, bot, True)
            if killstatus:
                bot.msg(self.mainchannel, kill.target+flipmsg+' has died tonight!', max_messages=10)
        # reset actionlist
        self.actionlist = []

    def BeginNightPhase(self, bot):
        self.votes = dict()
        for player in self.players:
            if not self.players[player].IsDead():
                self.votes[player] = self.NOVOTE
                self.players[player].BeginNightPhase(self, bot)
        self.phase = self.NIGHTPHASE
        self.factionkills = 1
        bot.msg(self.mainchannel, 'Night '+str(self.daycount)+' has started. Go to sleep and take required actions.', dict())
        for mafiach in self.mafiachannels:
            bot.msg(mafiach, 'You have '+str(self.factionkills)+' kills tonight. Use !kill <target> to use them. The player issuing the command will carry out the kill. Use !nokill to pass on the remaining faction kills for the night.', dict())

    # called every 5 seconds
    def GameLoop(self, bot):
        if self.joinchannels:
            for chn in self.mafiachannels:
                bot.join(chn)
                bot.write(('MODE ', chn+' +s', dict()))
            bot.join(self.deadchat)
            bot.join(self.mainchannel)
            self.joinchannels = False

        if self.active and (self.phase == self.NIGHTPHASE):
            # handle nightphase
            # check if there are more actions required to be taken
            requiredactions = False
            for player in self.players:
                if not self.players[player].IsDead():
                    if self.players[player].requiredaction == True:
                        requiredactions = True
            if self.factionkills > 0:
                requiredactions = True
            if not requiredactions:
                self.HandleActionList(bot)
                if not self.CheckForWinCondition(bot):
                    self.daycount += 1
                    self.phase = self.DAYPHASE
                    bot.msg(self.mainchannel, 'Day '+str(self.daycount)+' has just begun. The Town consists of '+self.GetPlayers())

