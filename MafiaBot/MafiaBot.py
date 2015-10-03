import random
import time
from MafiaPlayer import MafiaPlayer
from sopel.tools import Identifier
from MafiaAction import MafiaAction
from MafiaRole import MafiaRole
from Roles.rolelist import Roles
from Items.itemlist import Items
from MafiaSetup import MafiaSetup


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
        self.mainchannel = '#fridaynightmafia'
        self.joinchannels = False
        self.active = False
        self.phase = self.DAYPHASE
        self.votes = dict()
        self.actionlist = list()
        self.daycount = 1
        self.revealrolesondeath = True
        self.revealfactionondeath = True
        self.factionkills = 0
        self.setup = None
        self.time = time.clock()

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
        self.mafiachannels = ['#mafia'+str(random.randrange(10000))]
        self.players = dict()
        self.joinchannels = True
        self.active = False
        self.phase = self.DAYPHASE
        self.votes = dict()
        self.actionlist = list()
        self.daycount = 0
        self.revealrolesondeath = True
        self.revealfactionondeath = True
        self.factionkills = 0
        self.setup = MafiaSetup()
        self.time = time.clock()

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
                self[nick] = MafiaPlayer(nick)
                bot.msg(self.mainchannel, nick + ' has joined the game. There are currently '+str(len(self.players))+' Players in the game.')
            return None

        elif command == 'drop':
            if not self.active and nick in self.players:
                del self.players[nick]
                bot.msg(self.mainchannel, nick + ' has dropped from the game. There are currently '+str(len(self.players))+' Players in the game.')
            return None

        elif command == 'start':
            return self.StartGame(bot)

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

        elif command == 'time':
            if self.active and self.phase == self.DAYPHASE:
                timepassed = int(time.clock() - self.time)
                hours = timepassed / 3600
                minutes = (timepassed % 3600) / 60
                seconds = timepassed % 60
                return 'It has been '+str(hours).zfill(1)+':'+str(minutes).zfill(2)+':'+str(seconds).zfill(2)+' since the start of the day.'
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
                                if not self.players[identparam].IsDead() and not self.players[identparam].faction == MafiaPlayer.FACTION_MAFIA:
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

        elif command == 'item':
            if param.lower() in Items:
                return Items[param.lower()].ItemDescription()
            else:
                return 'I do not know the item '+param

        elif command == 'setup':
            if param == 'reset':
                self.setup = MafiaSetup()
                return "Reset setup!"
            else:
                return self.setup.HandleCommand(nick, param, self)

        elif command == 'roles':
            if self.active:
                if not source == nick and not source == self.deadchat:
                    return None
                if nick in self.players:
                    if not self.players[nick].IsDead():
                        return None
                # it is save to reply
                return 'The roles this game are - '+self.GetRoleList()
            return None

        # template
        elif command == '':
            return None

        return "I do not currently know how to handle command "+command

    def GetPlayers(self):
        msg = ''
        for player in self.players.keys():
            if self.active:
                # if game is going only add alive players
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
            # check if vote target is a player
            if Identifier(param) in self.players:
                # if he is alive we continue, otherwise we return
                if self.players[Identifier(param)].IsDead():
                    return
            # the only non player that is valid is NoLynch, otherwise we return
            elif not param == 'NoLynch':
                return
            self.votes[player] = param
            # check for majority
            cnt = 0
            for vote in self.votes.values():
                if vote.lower() == param.lower():
                    cnt += 1
            if cnt > len(self.votes)/2:
                # majority
                self.Lynch(Identifier(param), bot)
            else:
                # print current votes
                self.PrintVotes(bot)

    def PrintVotes(self, bot):
        msg = 'Current Votes -  '
        for pair in self.votes.items():
            if pair[1] == self.NOVOTE:
                msg += '\x02' + pair[0] + '\x02: No Vote '
            else:
                msg += '\x02' + pair[0] + '\x02: ' + pair[1] + ' '
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
        else:
            self.ResetGame()

    def CheckForWinCondition(self, bot):
        # check for victory condition
        townwin = True
        specialwin = False
        specialwinner = None
        mafiacount = 0
        nonmafiacount = 0
        nightkillpower = 0
        for player in self.players:
            if not self.players[player].IsDead():
                if self.players[player].faction == MafiaPlayer.FACTION_MAFIA:
                    mafiacount += 1
                else:
                    nonmafiacount += 1
                    nightkillpower += self.players[player].NightKillPower()
                if self.players[player].preventtownvictory:
                    townwin = False
                if self.players[player].CheckSpecialWinCondition(self):
                    specialwin = True
                    townwin = False
                    specialwinner = player

        # try our best to identify when mafia has won without claiming any early victories
        # mafia very rarely has forced wins when they are outnumbered, so calculations assume a no lynch as the strongest
        # day outcome, since mislynches are not enforceable
        if self.phase == self.NIGHTPHASE:
            if mafiacount > nonmafiacount:
                # if the mafia actually outnumber town going into the day, they can actually lynch a townie
                # ToDo: consider day guns once introduced
                nonmafiacount -= 1

        # now consider the outcome of the next night. Once mafia outnumber town, they can only be stopped by a large
        # amount of town kill power, which will be adjusted for each night check here
        # we assume the worst outcome for mafia, town uses all their nightkillpower on mafia, mafia kills a town
        # with no nightkillpower for the upcoming nights. If mafia then comes out having a majority, they should (almost)
        # always win the game.

        # if mafia numbers equal town going into the next day, usually mafia wins, but there are some drawing/allkill
        # scenarios we play it safe an continue the game for the time being
        mafiawin = (mafiacount >= nonmafiacount+nightkillpower)

        if townwin:
            self.active = False
            # get town players and prepare win message
            townies = [str(self.players[player].name) for player in self.players if self.players[player].faction == MafiaPlayer.FACTION_TOWN]
            playerstr = ', '.join(townies)
            bot.msg(self.mainchannel, 'Town wins this game! Congratulations to '+playerstr, max_messages=10)
            bot.msg(self.mainchannel, 'The roles this game were - '+self.GetRoleList(), max_messages=10)

        elif specialwin:
            self.active = False
            self.players[specialwinner].SpecialWin(self, bot)

        elif mafiawin:
            self.active = False
            # get mafia players and prepare win message
            mafia = [str(self.players[player].name) for player in self.players if (self.players[player].faction == MafiaPlayer.FACTION_MAFIA or self.players[player].faction == MafiaPlayer.FACTION_MAFIATRAITOR)]
            playerstr = ', '.join(mafia)
            bot.msg(self.mainchannel, 'Mafia wins this game! Congratulations to '+playerstr, max_messages=10)
            bot.msg(self.mainchannel, 'The roles this game were - '+self.GetRoleList(), max_messages=10)

        return mafiawin or townwin

    def StartGame(self, bot):
        # check if the right number of players are in the game
        requiredplayers = self.setup.GetRequiredPlayers()
        if requiredplayers > 0:
            if not len(self.players) == requiredplayers:
                return 'This setup requires '+str(requiredplayers)+' players. There are currenty '+str(len(self.players))+' players signed up for the game.'
        self.active = True
        self.time = time.clock()
        self.votes = dict()
        self.revealrolesondeath = self.setup.revealrole
        self.revealfactionondeath = self.setup.revealfaction
        self.AssignRoles()
        for player in self.players.keys():
            self[player].dead = False
            self.votes[player] = self.NOVOTE
            if self[player].role is not None:
                self[player].role.StartGame(bot, self[player], self)
            # send role PM to all of the players
            bot.msg(player, self[player].GetRolePM())
        bot.msg(self.mainchannel, 'The game has started!')
        if self.setup.GetDaystart():
            bot.msg(self.mainchannel, 'It is now day 0.')
        else:
            self.BeginNightPhase(bot)
        return None

    def AssignRoles(self):
        rolelist = self.setup.GetRoleList(self)
        random.shuffle(rolelist)
        # assign roles to players
        i = 0
        for player in self.players.values():
            # set faction
            player.faction = rolelist[i][0]
            if player.faction == MafiaPlayer.FACTION_MAFIA:
                player.mafiachannel = self.mafiachannels[0]
                player.preventtownvictory = True
            elif player.faction == MafiaPlayer.FACTION_THIRDPARTY:
                player.preventtownvictory = player.role.preventtownvictory
            # instantiate role
            if rolelist[i][1] is not None:
                # create role
                if rolelist[i][1] in Roles:
                    player.role = Roles[rolelist[i][1]](rolelist[i][2])
                else:
                    # create dummy role
                    player.role = MafiaRole()
            i += 1

    def HandleActionList(self, bot):
        # shuffle action list so there's no information to be gathered from multiple events happening in the same night
        random.shuffle(self.actionlist)

        # handle roleblocks
        blockset = set([action.target for action in self.actionlist if action.actiontype == MafiaAction.BLOCK])

        # handle protections
        protections = [action for action in self.actionlist if action.actiontype == MafiaAction.PROTECT and action.source not in blockset]
        protectdict = dict()
        for protect in protections:
            if protect.target not in protectdict:
                protectdict[protect.target] = 1
            else:
                protectdict[protect.target] += 1
        # handle faction investigations
        copchecks = [action for action in self.actionlist if action.actiontype == MafiaAction.CHECKFACTION]
        for check in copchecks:
            if check.source in blockset:
                bot.msg(check.source, 'You were blocked tonight.')
            else:
                faction = self.players[check.target].GetFaction()
                if 'sanity' in check.modifiers:
                    sanity = check.modifiers['sanity']
                    if sanity == 'insane':
                        if faction == 'Town':
                            faction = 'Mafia'
                        elif faction == 'Mafia':
                            faction = 'Town'
                    elif sanity == 'naive':
                        faction = 'Town'
                    elif sanity == 'paranoid':
                        faction = 'Mafia'
                    elif sanity == 'random':
                        rnd = random.randint(1, 2)
                        if rnd == 1:
                            faction = 'Town'
                        else:
                            faction = 'Mafia'

                bot.msg(check.source, 'Your investigation on '+str(check.target)+' reveals him to be aligned with '+faction+'.')

        # handle item receptions
        itemsends = [action for action in self.actionlist if action.actiontype == MafiaAction.SENDITEM and action.source not in blockset]
        for send in itemsends:
            self.players[send.target].ReceiveItem(send.modifiers['item'], bot, self)

        # handle role investigations
        rolecopchecks = [action for action in self.actionlist if action.actiontype == MafiaAction.CHECKROLE]
        for check in rolecopchecks:
            if check.source in blockset:
                bot.msg(check.source, 'You were blocked tonight.')
            else:
                if self.players[check.target].role is not None:
                    rolename = self.players[check.target].role.GetRoleName()
                    if rolename == 'Goon' or rolename == 'Civilian':
                        rolename = 'Vanilla'
                    else:
                        rolename = 'a '+rolename
                    bot.msg(check.source, 'Your investigation on '+str(check.target)+' reveals him to be '+rolename+'.')
                else:
                    bot.msg(check.source, 'Your investigation on '+str(check.target)+' reveals him to not have a role at all. Strange.')

        # handle trackings
        tracks = [action for action in self.actionlist if action.actiontype == MafiaAction.TRACK]
        for track in tracks:
            if track.source in blockset:
                bot.msg(track.source, 'You were blocked tonight.')
            else:
                visits = [action.target for action in self.actionlist if (action.source == track.target and action.visiting and (action.actiontype == MafiaAction.BLOCK or action.source not in blockset))]
                if visits:
                    bot.msg(track.source, str(track.target)+' visited the following players tonight: '+', '.join(visits))
                else:
                    bot.msg(track.source, str(track.target)+' did not visit anybody tonight.')
                    
        # handle watches
        watchs = [action for action in self.actionlist if action.actiontype == MafiaAction.WATCH]
        for watch in watchs:
            if watch.source in blockset:
                bot.msg(watch.source, 'You were blocked tonight.')
            else:
                visits = [action.source for action in self.actionlist if (action.target == watch.target and not action.source == watch.source and action.visiting and (action.actiontype == MafiaAction.BLOCK or action.source not in blockset))]
                if visits:
                    bot.msg(watch.source, str(watch.target)+' was visited by the following players tonight: '+', '.join(visits))
                else:
                    bot.msg(watch.source, str(watch.target)+' was not visited tonight.')

        # handle callback actions
        callbacks = [action for action in self.actionlist if action.actiontype == MafiaAction.CALLBACK]
        for callback in callbacks:
            if callback.source not in blockset:
                callback.modifiers['callback'](callback.source, bot, self)

        # handle kill actions
        nokills = True
        killlist = [action for action in self.actionlist if action.actiontype == MafiaAction.KILL and action.source not in blockset]
        for kill in killlist:
            # check if a player was protected
            skip = False
            if kill.target in protectdict:
                if protectdict[kill.target] > 0:
                    protectdict[kill.target] -= 1
                    skip = True
            if not skip:
                killstatus, flipmsg = self.players[kill.target].Kill(self, bot, True)
                if killstatus:
                    nokills = False
                    bot.msg(self.mainchannel, kill.target+flipmsg+' has died tonight!', max_messages=10)
        if nokills:
            bot.msg(self.mainchannel, 'Nobody has died tonight!', max_messages=10)
        # reset actionlist
        self.actionlist = []

    def GetRoleList(self):
        retstr = ''
        for player in self.players.values():
            if player.IsDead():
                deadstr = ' (Dead)'
            else:
                deadstr = ''
            factionstr = player.GetFaction()
            if player.role is not None:
                rolestr = player.role.GetRoleName()
            else:
                rolestr = ''
            # include cop sanities:
            if rolestr == 'Cop':
                rolestr += ' ('+player.role.sanity+')'
            retstr += '\x02' + str(player.name) + '\x02' + deadstr + ': ' + factionstr + ' ' + rolestr + '  '
        return retstr.rstrip()

    def BeginNightPhase(self, bot):
        self.daycount += 1
        self.phase = self.NIGHTPHASE
        bot.msg(self.mainchannel, 'Night '+str(self.daycount)+' has started. Go to sleep and take required actions.')
        self.votes = dict()
        for player in self.players:
            if not self.players[player].IsDead():
                self.votes[player] = self.NOVOTE
                self.players[player].BeginNightPhase(self, bot)
        self.factionkills = 1
        for mafiach in self.mafiachannels:
            bot.msg(mafiach, 'You have '+str(self.factionkills)+' kills tonight. Use !kill <target> to use them. The player issuing the command will carry out the kill. Use !nokill to pass on the remaining faction kills for the night.')

    # called every 5 seconds
    def GameLoop(self, bot):
        if self.joinchannels:
            for chn in self.mafiachannels:
                bot.join(chn)
                bot.write(('MODE ', chn+' +s'))
            bot.join(self.deadchat)
            bot.join(self.mainchannel)
            self.joinchannels = False

        if self.active and (self.phase == self.NIGHTPHASE):
            # handle nightphase
            # check if there are more actions required to be taken
            requiredactions = False
            for player in self.players:
                if not self.players[player].IsDead():
                    if self.players[player].requiredaction:
                        requiredactions = True
            if self.factionkills > 0:
                requiredactions = True
            if not requiredactions:
                self.HandleActionList(bot)
                if not self.CheckForWinCondition(bot):
                    self.phase = self.DAYPHASE
                    self.time = time.clock()
                    # reset votes
                    self.votes = dict()
                    for player in self.players:
                        if not self.players[player].IsDead():
                            self.votes[player] = self.NOVOTE
                    bot.msg(self.mainchannel, 'Day '+str(self.daycount)+' has just begun. The Town consists of '+self.GetPlayers())
                else:
                    self.ResetGame()
