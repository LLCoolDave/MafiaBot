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

    def _getPlayer(self, name):
        try:
            return self.players[Identifier(name)]
        except:
            return None

    def _isPlayer(self, name):
        return Identifier(name) in self.players

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
        player = self._getPlayer(nick)
        if player is not None:
            if not player.IsDead():
                return player.HandleCommand(command.lower(), param, bot, self)
        return None

    def HandleCommand(self, command, source, nick, param, bot):

        command = command.lower()

        if param is not None:
            param = param.rstrip()
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
            if self.active:
                return "The deadchat is at "+self.deadchat

        elif command == 'join':
            if not self.active and not self._isPlayer(nick):
                if Identifier(nick) == 'NoLynch':
                    return 'NoLynch is a restricted name and cannot be used. Please join under a different nickname.'
                self[Identifier(nick)] = MafiaPlayer(Identifier(nick))
                bot.msg(self.mainchannel, nick + ' has joined the game. There are currently '+str(len(self.players))+' Players in the game.')
            return None

        elif command == 'drop':
            if not self.active and self._isPlayer(nick):
                del self.players[Identifier(nick)]
                bot.msg(self.mainchannel, nick + ' has dropped from the game. There are currently '+str(len(self.players))+' Players in the game.')
            return None

        elif command == 'start':
            return self.StartGame(bot)

        elif command == 'vote':
            if self.active and self.phase == self.DAYPHASE and self._isPlayer(nick):
                self.HandleVote(nick, param, bot)
                return None
            else:
                return None

        elif command == 'nolynch':
            if self.active and self.phase == self.DAYPHASE and self._isPlayer(nick):
                self.HandleVote(nick, 'NoLynch', bot)
                return None
            else:
                return None

        elif command == 'unvote':
            if self.active and self._isPlayer(nick):
                self.votes[Identifier(nick)] = (self.NOVOTE, time.clock())
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
            player = self._getPlayer(nick)
            if player is not None and str(source) in self.mafiachannels:
                # check if it is night
                if self.phase == self.NIGHTPHASE:
                    # check if player is alive and mafia
                    if not player.IsDead() and player.faction == MafiaPlayer.FACTION_MAFIA:
                        # check if there are kills left
                        if self.factionkills <= 0:
                            return 'There are no faction kills left to be carried out tonight.'
                        else:
                            # check if player exists, is alive
                            target = self._getPlayer(param)
                            if target is not None:
                                if not target.IsDead() and not target.faction == MafiaPlayer.FACTION_MAFIA:
                                    # player can be killed, so we add the action
                                    self.actionlist.append(MafiaAction(MafiaAction.KILL, nick, param, True))
                                    self.factionkills -= 1
                                    return nick+' will kill '+param+' tonight.'

                            # couldn't find valid kill target
                            return param + ' is not a player that can be killed!'
            return None

        elif command == 'nokill':
            # check if message came from a mafia channel
            player = self._getPlayer(nick)
            if player is not None and str(source) in self.mafiachannels:
                # check if it is night
                if self.phase == self.NIGHTPHASE:
                    # check if player is alive and mafia
                    if not player.IsDead() and player.faction == MafiaPlayer.FACTION_MAFIA:
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
                player = self._getPlayer(nick)
                if player is not None:
                    if not player.IsDead():
                        return None
                # it is save to reply
                return 'The roles this game are - '+self.GetRoleList()
            return None

        elif command == 'dice':
            try:
                limit = int(param)
                result = random.randint(1, limit)
                if limit == 2:
                    if result == 1:
                        return 'The coin comes up: Heads'
                    else:
                        return 'The coin comes up: Tails'
                else:
                    return 'You roll a d%u, the result is a %u.' % (limit, result)
            except:
                return None

        # template
        elif command == '':
            return None

        return "I do not currently know how to handle command "+command

    def GetPlayers(self):
        players = []
        for player in self.players.items():
            if self.active:
                # if game is going only add alive players
                if not player[1].IsDead():
                    players.append(player[0])
            else:
                players.append(player[0])
        return ', '.join(players)

    def GetChannels(self):
        return list(self.mafiachannels).append(self.deadchat)

    def IsDead(self, player):
        try:
            return self._getPlayer(player).IsDead()
        except:
            return True

    def MayJoin(self, nick, channel):
        player = self._getPlayer(nick)
        if player is not None:
            if player.mafiachannel == channel:
                return True
            else:
                return False
        else:
            return False

    def HandleVote(self, nick, param, bot):
        player = self._getPlayer(nick)
        # we know nick matches a player at this point
        if not player.IsDead():
            # check if vote target is a player
            if self._isPlayer(param):
                # if he is alive we continue, otherwise we return
                if self._getPlayer(param).IsDead():
                    return
            # the only non player that is valid is NoLynch, otherwise we return
            elif not param == 'NoLynch':
                return
            self.votes[Identifier(nick)] = (Identifier(param), time.clock())
            # check for majority
            cnt = 0
            for vote in self.votes.values():
                if vote[0] == param:
                    cnt += 1
            if cnt > len(self.votes)/2:
                # majority
                self.Lynch(param, bot)
            else:
                # print current votes
                self.PrintVotes(bot)

    def PrintVotes(self, bot):
        votecounter = {}
        for pair in self.votes.items():
            if pair[1][0] not in votecounter:
                votecounter[pair[1][0]] = []
            votecounter[pair[1][0]].append((pair[0], pair[1][1]))
        sortedvotelist = sorted(votecounter.items(), key=lambda x: -len(x[1]) if not x[0] == '' else 1)
        votestr = ' - '.join(['\x02%s (%u)\x02: %s' % (target if not target == '' else 'No Vote', len(votelist), ', '.join([voter[0] for voter in sorted(votelist, key=lambda x: x[1])])) for target, votelist in sortedvotelist])
        msg = 'Current Votes - %s - \x02%s\x02 votes required for a lynch.' % (votestr, len(self.votes)/2 + 1)
        bot.msg(self.mainchannel, msg, max_messages=10)

    def Lynch(self, nick, bot):
        if nick == 'NoLynch':
            bot.msg(self.mainchannel, 'The town decides not to lynch anybody today.', max_messages=10)
        else:
            player = self._getPlayer(nick)
            killok, playerflip = player.Kill(self, bot, False)
            if killok:
                bot.msg(self.mainchannel, nick+playerflip+' was lynched today!', max_messages=10)
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
        for player in self.players.values():
            if not player.IsDead():
                if player.faction == MafiaPlayer.FACTION_MAFIA:
                    mafiacount += 1
                else:
                    nonmafiacount += 1
                    nightkillpower += player.NightKillPower()
                if player.preventtownvictory:
                    townwin = False
                if player.CheckSpecialWinCondition(self):
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
            townies = [nick for nick, player in self.players.items() if player.faction == MafiaPlayer.FACTION_TOWN]
            playerstr = ', '.join(townies)
            bot.msg(self.mainchannel, 'Town wins this game! Congratulations to '+playerstr, max_messages=10)
            bot.msg(self.mainchannel, 'The roles this game were - '+self.GetRoleList(), max_messages=10)

        elif specialwin:
            self.active = False
            specialwinner.SpecialWin(specialwinner, self, bot)

        elif mafiawin:
            self.active = False
            # get mafia players and prepare win message
            mafia = [nick for nick, player in self.players.items() if (player.faction == MafiaPlayer.FACTION_MAFIA or player.faction == MafiaPlayer.FACTION_MAFIATRAITOR)]
            playerstr = ', '.join(mafia)
            bot.msg(self.mainchannel, 'Mafia wins this game! Congratulations to '+playerstr, max_messages=10)
            bot.msg(self.mainchannel, 'The roles this game were - '+self.GetRoleList(), max_messages=10)

        return mafiawin or townwin or specialwin

    def StartGame(self, bot):
        # check if the right number of players are in the game
        requiredplayers = self.setup.GetRequiredPlayers()
        if requiredplayers is None:
            return 'No Setup for this game entered. You cannot start yet.'
        if requiredplayers > 0:
            if not len(self.players) == requiredplayers:
                return 'This setup requires '+str(requiredplayers)+' players. There are currenty '+str(len(self.players))+' players signed up for the game.'
        bot.msg(self.mainchannel, 'The game is starting!')
        self.active = True
        self.time = time.clock()
        self.votes = dict()
        self.revealrolesondeath = self.setup.revealrole
        self.revealfactionondeath = self.setup.revealfaction
        self.AssignRoles()
        for nick, player in self.players.items():
            player.dead = False
            self.votes[Identifier(nick)] = (self.NOVOTE, time.clock())
            # send role PM to all of the players
            bot.msg(nick, player.GetRolePM())
            if player.role is not None:
                player.role.StartGame(bot, player, self)
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

        # build log of night actions:
        nighthistory = ''
        for action in self.actionlist:
            nighthistory += '\x02'+MafiaAction.Lookup[action.actiontype]+'\x02 by '+action.source+' on '+action.target+' '
            if action.actiontype == MafiaAction.SENDITEM:
                nighthistory += 'with '+action.modifiers['item']+' '

        # handle roleblocks
        preblockset = {action for action in self.actionlist if action.actiontype == MafiaAction.BLOCK}
        # first build up people blocking from non town sources
        blockset = {Identifier(action.target) for action in preblockset if not action.modifiers['faction'] == MafiaPlayer.FACTION_TOWN}
        # then add blocks that are town sourced but not blocked
        blockset = blockset.union({Identifier(action.target) for action in preblockset if Identifier(action.source) not in blockset})

        # handle protections
        protections = [action for action in self.actionlist if action.actiontype == MafiaAction.PROTECT and Identifier(action.source) not in blockset]
        protectdict = dict()
        for protect in protections:
            if Identifier(protect.target) not in protectdict:
                protectdict[Identifier(protect.target)] = 1
            else:
                protectdict[Identifier(protect.target)] += 1
        # handle faction investigations
        copchecks = [action for action in self.actionlist if action.actiontype == MafiaAction.CHECKFACTION]
        for check in copchecks:
            if Identifier(check.source) in blockset:
                bot.msg(check.source, 'You were blocked tonight.')
            else:
                faction = self._getPlayer(check.target).GetFaction()
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
        itemsends = [action for action in self.actionlist if action.actiontype == MafiaAction.SENDITEM and Identifier(action.source) not in blockset]
        for send in itemsends:
            self._getPlayer(send.target).ReceiveItem(send.modifiers['item'], bot, self)

        # handle role investigations
        rolecopchecks = [action for action in self.actionlist if action.actiontype == MafiaAction.CHECKROLE]
        for check in rolecopchecks:
            if Identifier(check.source) in blockset:
                bot.msg(check.source, 'You were blocked tonight.')
            else:
                if self._getPlayer(check.target).role is not None:
                    rolename = self._getPlayer(check.target).role.GetRoleName()
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
            if Identifier(track.source) in blockset:
                bot.msg(track.source, 'You were blocked tonight.')
            else:
                visits = [Identifier(action.target) for action in self.actionlist if (Identifier(action.source) == Identifier(track.target) and action.visiting and (action.actiontype == MafiaAction.BLOCK or Identifier(action.source) not in blockset))]
                if visits:
                    bot.msg(track.source, str(track.target)+' visited the following players tonight: '+', '.join(visits))
                else:
                    bot.msg(track.source, str(track.target)+' did not visit anybody tonight.')
                    
        # handle watches
        watchs = [action for action in self.actionlist if action.actiontype == MafiaAction.WATCH]
        for watch in watchs:
            if Identifier(watch.source) in blockset:
                bot.msg(watch.source, 'You were blocked tonight.')
            else:
                visits = [Identifier(action.source) for action in self.actionlist if (Identifier(action.target) == Identifier(watch.target) and not Identifier(action.source) == Identifier(watch.source) and action.visiting and (action.actiontype == MafiaAction.BLOCK or Identifier(action.source) not in blockset))]
                if visits:
                    bot.msg(watch.source, str(watch.target)+' was visited by the following players tonight: '+', '.join(visits))
                else:
                    bot.msg(watch.source, str(watch.target)+' was not visited tonight.')

        # handle callback actions
        callbacks = [action for action in self.actionlist if action.actiontype == MafiaAction.CALLBACK]
        for callback in callbacks:
            if Identifier(callback.source) in blockset:
                blocked = True
            else:
                blocked = False
            callback.modifiers['callback'](Identifier(callback.source), bot, self, blocked)

        # handle kill actions
        nokills = True
        killlist = [action for action in self.actionlist if action.actiontype == MafiaAction.KILL and Identifier(action.source) not in blockset]
        for kill in killlist:
            # check if a player was protected
            skip = False
            if Identifier(kill.target) in protectdict:
                if protectdict[Identifier(kill.target)] > 0:
                    protectdict[Identifier(kill.target)] -= 1
                    skip = True
            if not skip:
                killstatus, flipmsg = self._getPlayer(kill.target).Kill(self, bot, True)
                if killstatus:
                    nokills = False
                    bot.msg(self.mainchannel, kill.target+flipmsg+' has died tonight!', max_messages=10)
        if nokills:
            bot.msg(self.mainchannel, 'Nobody has died tonight!', max_messages=10)
        # reset actionlist
        self.actionlist = []
        # send history to deadchat
        bot.msg(self.deadchat, nighthistory, max_messages=10)

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
        for nick, player in self.players.items():
            if not player.IsDead():
                self.votes[Identifier(nick)] = (self.NOVOTE, time.clock())
                player.BeginNightPhase(self, bot)
        self.factionkills = self.GetNightKillPower()
        for mafiach in self.mafiachannels:
            bot.msg(mafiach, 'You have '+str(self.factionkills)+' kills tonight. Use !kill <target> to use them. The player issuing the command will carry out the kill. Use !nokill to pass on the remaining faction kills for the night.')

    def GetNightKillPower(self):
        if self.setup.killpowerreduction is not None:
            mafiacount = 0
            playercount = 0
            for player in self.players.values():
                if not player.IsDead():
                    playercount += 1
                    if player.faction == MafiaPlayer.FACTION_MAFIA:
                        mafiacount += 1
            if self.setup.killpowerreduction[0] == MafiaSetup.REDUCTION_MAFIA:
                if mafiacount <= self.setup.killpowerreduction[1]:
                    return 1
                else:
                    return self.setup.mafiakillpower
            elif self.setup.killpowerreduction[0] == MafiaSetup.REDUCTION_PLAYERS:
                if playercount <= self.setup.killpowerreduction[1]:
                    return 1
                else:
                    return self.setup.mafiakillpower
        return self.setup.mafiakillpower

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
            for player in self.players.values():
                if not player.IsDead():
                    if player.requiredaction or player.afk:
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
                    for nick, player in self.players.items():
                        if not player.IsDead():
                            self.votes[Identifier(nick)] = (self.NOVOTE, time.clock())
                    bot.msg(self.mainchannel, 'Day '+str(self.daycount)+' has just begun. The Town consists of '+self.GetPlayers())
                else:
                    self.ResetGame()
