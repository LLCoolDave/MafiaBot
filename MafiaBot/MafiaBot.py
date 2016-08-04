import random
import time
from .MafiaPlayer import MafiaPlayer
from .MafiaAction import MafiaAction
from .MafiaRole import MafiaRole
from .Roles.rolelist import Roles
from .Items.itemlist import Items
from .MafiaSetup import MafiaSetup


class MafiaBot:

    DAWN = 0
    DAYPHASE = 1
    DUSK = 2
    NIGHTPHASE = 3

    PhaseStr = {0: 'Dawn', 1: 'Day', 2: 'Dusk', 3: 'Night'}

    NOVOTE = ''

    def __init__(self, communication):
        self.communication = communication
        self.deadchat = ''
        self.mafiachannels = []
        self.players = dict()
        self.mainchannel = self.communication.get_game_channel()
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

    def Send(self, target, message, **kwargs):
        self.communication.send(target, message, **kwargs)

    def Action(self, *varargs):
        self.communication.action(*varargs)

    def JoinChannel(self, channel):
        self.communication.join(channel)

    def LeaveChannel(self, channel):
        self.communication.leave(channel)

    def GetPlayer(self, name):
        try:
            return self.players[self.communication.get_id(name)]
        except:
            return None

    def _isPlayer(self, name):
        return self.communication.get_id(name) in self.players

    def ResetGame(self):
        self.deadchat = self.communication.get_dead_chat()
        self.mafiachannels = self.communication.get_mafia_chat()
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

    def HandlePlayerCommand(self, command, nick, param):
        player = self.GetPlayer(nick)
        if player is not None:
            if not player.IsDead():
                response = player.HandleCommand(command.lower(), param, self)
                if response is not None:
                    self.Send(nick, response)

    def HandleCommand(self, command, source, nick, param):

        command = command.lower()

        if param is not None:
            param = param.rstrip()
        if command == 'abort':
            # leave active channels
            for chn in self.mafiachannels:
                self.LeaveChannel(chn)
            self.LeaveChannel(self.deadchat)
            self.ResetGame()
            # rejoin new channels and set silent mode for mafia channels
            for chn in self.mafiachannels:
                self.JoinChannel(chn)
                self.Action('MODE ', chn+' +s')
            self.JoinChannel(self.deadchat)

        elif command == 'deadchat':
            if self.active:
                self.Send(source, "The deadchat is at "+str(self.deadchat))

        elif command == 'join':
            if not self.active and not self._isPlayer(nick):
                if nick.lower() == 'nolynch':
                    self.Send(source, 'NoLynch is a restricted name and cannot be used. Please join under a different nickname.')
                    return
                self[self.communication.get_id(nick)] = MafiaPlayer(str(nick))
                self.Send(self.mainchannel, nick + ' has joined the game. There are currently '+str(len(self.players))+' Players in the game.')

        elif command == 'drop':
            if not self.active and self._isPlayer(nick):
                del self.players[self.communication.get_id(nick)]
                self.Send(self.mainchannel, nick + ' has dropped from the game. There are currently '+str(len(self.players))+' Players in the game.')

        elif command == 'start':
            self.Send(source, self.StartGame())

        elif command == 'vote':
            if self.active and self.phase == self.DAYPHASE and self._isPlayer(nick):
                self.HandleVote(nick, param)

        elif command == 'nolynch':
            if self.active and self.phase == self.DAYPHASE and self._isPlayer(nick):
                self.HandleVote(nick, 'NoLynch')

        elif command == 'unvote':
            if self.active and self._isPlayer(nick):
                self.votes[self.GetPlayer(nick)] = (self.NOVOTE, time.clock())
                self.PrintVotes()

        elif command == 'votes':
            if self.active and self.phase == self.DAYPHASE:
                self.PrintVotes()

        elif command == 'time':
            if self.active and self.phase == self.DAYPHASE:
                timepassed = int(time.clock() - self.time)
                hours = timepassed / 3600
                minutes = (timepassed % 3600) / 60
                seconds = timepassed % 60
                self.Send(source, 'It has been '+str(hours).zfill(1)+':'+str(minutes).zfill(2)+':'+str(seconds).zfill(2)+' since the start of the day.')

        elif command == 'players':
            if not self.players:
                self.Send(source, 'No players active')
            else:
                self.Send(source, 'Playerlist: ' + self.GetPlayers())

        elif command == 'kill':
            # check if message came from a mafia channel
            player = self.GetPlayer(nick)
            if player is not None and str(source) in self.mafiachannels:
                # check if it is night
                if self.phase == self.NIGHTPHASE:
                    # check if player is alive and mafia
                    if not player.IsDead() and player.faction == MafiaPlayer.FACTION_MAFIA:
                        # check if there are kills left
                        if self.factionkills <= 0:
                            self.Send(source, 'There are no faction kills left to be carried out tonight.')
                        else:
                            # check if player exists, is alive
                            target = self.GetPlayer(param)
                            if target is not None:
                                if not target.IsDead() and not target.faction == MafiaPlayer.FACTION_MAFIA:
                                    # player can be killed, so we add the action
                                    self.actionlist.append(MafiaAction(MafiaAction.KILL, player, target, True))
                                    self.factionkills -= 1
                                    self.Send(source, nick+' will kill '+param+' tonight.')

                            # couldn't find valid kill target
                            self.Send(source, param + ' is not a player that can be killed!')

        elif command == 'nokill':
            # check if message came from a mafia channel
            player = self.GetPlayer(nick)
            if player is not None and str(source) in self.mafiachannels:
                # check if it is night
                if self.phase == self.NIGHTPHASE:
                    # check if player is alive and mafia
                    if not player.IsDead() and player.faction == MafiaPlayer.FACTION_MAFIA:
                        # check if there are kills left
                        if self.factionkills <= 0:
                            self.Send(source, 'There are no faction kills left to be carried out tonight.')
                        else:
                            # pass remaining kills
                            self.factionkills = 0
                            self.Send(source, 'You forgo any outstanding faction kills for the night.')
            return None

        elif command == 'phase':
            if self.active:
                self.Send(source, 'It is currently '+self.PhaseStr[self.phase]+' on Day '+str(self.daycount))

        elif command == 'role':
            if param:
                if param.lower() in Roles:
                    self.Send(source, Roles[param.lower()].GetRoleDescription())
                else:
                    self.Send(source, 'I do not know the role '+param)

        elif command == 'item':
            if param:
                if param.lower() in Items:
                    self.Send(source, Items[param.lower()].ItemDescription())
                else:
                    self.Send(source, 'I do not know the item '+param)

        elif command == 'setup':
            if param == 'reset':
                self.setup = MafiaSetup()
                self.Send(source, "Reset setup!")
            else:
                self.Send(source, self.setup.HandleCommand(nick, param, self))

        elif command == 'roles':
            if self.active:
                safereply = False
                if source == self.deadchat:
                    safereply = True
                elif source == nick:
                    player = self.GetPlayer(nick)
                    if player is not None:
                        if player.IsDead():
                            safereply = True
                    else:
                        safereply = True
                if safereply:
                    # it is save to reply
                    self.Send(source, 'The roles this game are - '+self.GetRoleList())

        elif command == 'dice':
            try:
                limit = int(param)
                result = random.randint(1, limit)
                if limit == 2:
                    if result == 1:
                        self.Send(source, 'The coin comes up: Heads')
                    else:
                        self.Send(source, 'The coin comes up: Tails')
                else:
                    self.Send(source, 'You roll a d%u, the result is a %u.' % (limit, result))
            except:
                pass

        # template
        elif command == '':
            pass

        else:
            self.Send(source, "I do not currently know how to handle command "+command)

    def GetPlayers(self):
        players = []
        for player in self.players.values():
            if self.active:
                # if game is going only add alive players
                if not player.IsDead():
                    players.append(str(player))
            else:
                players.append(str(player))
        return ', '.join(players)

    def GetChannels(self):
        return list(self.mafiachannels).append(self.deadchat)

    def IsDead(self, player):
        try:
            return self.GetPlayer(player).IsDead()
        except:
            return True

    def MayJoin(self, nick, channel):
        player = self.GetPlayer(nick)
        if player is not None:
            if player.mafiachannel == channel:
                return True
            else:
                return False
        else:
            return False

    def HandleVote(self, nick, param):
        player = self.GetPlayer(nick)
        # we know nick matches a player at this point
        if not player.IsDead():
            # check if vote target is a player
            if self._isPlayer(param):
                # if he is alive we continue, otherwise we return
                if self.GetPlayer(param).IsDead():
                    return
                else:
                    param = self.GetPlayer(param)
            # the only non player that is valid is NoLynch, otherwise we return
            elif not param == 'NoLynch':
                return
            self.votes[player] = (param, time.clock())
            # check for majority
            cnt = 0
            for vote in self.votes.values():
                if vote[0] == param:
                    cnt += 1
            if cnt > len(self.votes)/2:
                # majority
                self.Lynch(param)
            else:
                # print current votes
                self.PrintVotes()

    def PrintVotes(self):
        votecounter = {}
        for pair in self.votes.items():
            if pair[1][0] not in votecounter:
                votecounter[pair[1][0]] = []
            votecounter[pair[1][0]].append((pair[0], pair[1][1]))
        sortedvotelist = sorted(votecounter.items(), key=lambda x: -len(x[1]) if not x[0] == '' else 1)
        votestr = ' - '.join(['\x02%s (%u)\x02: %s' % (str(target) if not target == '' else 'No Vote', len(votelist), ', '.join([str(voter[0]) for voter in sorted(votelist, key=lambda x: x[1])])) for target, votelist in sortedvotelist])
        msg = 'Current Votes - %s - \x02%s\x02 votes required for a lynch.' % (votestr, len(self.votes)/2 + 1)
        self.Send(self.mainchannel, msg, max_messages=10)

    def Lynch(self, nick):
        if nick == 'NoLynch':
            self.Send(self.mainchannel, 'The town decides not to lynch anybody today.', max_messages=10)
        else:
            player = nick
            killok, playerflip = player.Kill(self, False)
            if killok:
                self.Send(self.mainchannel, str(nick)+playerflip+' was lynched today!', max_messages=10)
        if not self.CheckForWinCondition():
            self.BeginNightPhase()
        else:
            self.ResetGame()

    def CheckForWinCondition(self):
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
            townies = [str(player) for player in self.players.values() if player.faction == MafiaPlayer.FACTION_TOWN]
            playerstr = ', '.join(townies)
            self.Send(self.mainchannel, 'Town wins this game! Congratulations to '+playerstr, max_messages=10)
            self.Send(self.mainchannel, 'The roles this game were - '+self.GetRoleList(), max_messages=10)

        elif specialwin:
            self.active = False
            specialwinner.SpecialWin(specialwinner, self)

        elif mafiawin:
            self.active = False
            # get mafia players and prepare win message
            mafia = [str(player) for player in self.players.values() if (player.faction == MafiaPlayer.FACTION_MAFIA or player.faction == MafiaPlayer.FACTION_MAFIATRAITOR)]
            playerstr = ', '.join(mafia)
            self.Send(self.mainchannel, 'Mafia wins this game! Congratulations to '+playerstr, max_messages=10)
            self.Send(self.mainchannel, 'The roles this game were - '+self.GetRoleList(), max_messages=10)

        return mafiawin or townwin or specialwin

    def StartGame(self):
        # check if the right number of players are in the game
        requiredplayers = self.setup.GetRequiredPlayers()
        if requiredplayers is None:
            return 'No Setup for this game entered. You cannot start yet.'
        if requiredplayers > 0:
            if not len(self.players) == requiredplayers:
                return 'This setup requires '+str(requiredplayers)+' players. There are currenty '+str(len(self.players))+' players signed up for the game.'
        self.Send(self.mainchannel, 'The game is starting!')
        self.active = True
        self.time = time.clock()
        self.votes = dict()
        self.revealrolesondeath = self.setup.revealrole
        self.revealfactionondeath = self.setup.revealfaction
        self.AssignRoles()
        for player in self.players.values():
            player.dead = False
            self.votes[player] = (self.NOVOTE, time.clock())
            # send role PM to all of the players
            self.Send(player, player.GetRolePM())
            if player.role is not None:
                player.role.StartGame(player, self)
        if self.setup.GetDaystart():
            self.Send(self.mainchannel, 'It is now day 0.')
        else:
            self.BeginNightPhase()
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

    def HandleActionList(self):
        # shuffle action list so there's no information to be gathered from multiple events happening in the same night
        random.shuffle(self.actionlist)

        # build log of night actions:
        nighthistory = ''
        for action in self.actionlist:
            nighthistory += '\x02'+MafiaAction.Lookup[action.actiontype]+'\x02 by '+str(action.source)+' on '+str(action.target)+' '
            if action.actiontype == MafiaAction.SENDITEM:
                nighthistory += 'with '+action.modifiers['item']+' '

        # handle roleblocks
        preblockset = {action for action in self.actionlist if action.actiontype == MafiaAction.BLOCK}
        # first build up people blocking from non town sources
        blockset = {action.target for action in preblockset if not action.modifiers['faction'] == MafiaPlayer.FACTION_TOWN}
        # then add blocks that are town sourced but not blocked
        blockset = blockset.union({action.target for action in preblockset if action.source not in blockset})

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
                self.Send(check.source, 'You were blocked tonight.')
            else:
                faction = check.target.GetFaction()
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

                self.Send(check.source, 'Your investigation on '+str(check.target)+' reveals him to be aligned with '+faction+'.')

        # handle item receptions
        itemsends = [action for action in self.actionlist if action.actiontype == MafiaAction.SENDITEM and action.source not in blockset]
        for send in itemsends:
            send.target.ReceiveItem(send.modifiers['item'], self)

        # handle role investigations
        rolecopchecks = [action for action in self.actionlist if action.actiontype == MafiaAction.CHECKROLE]
        for check in rolecopchecks:
            if check.source in blockset:
                self.Send(check.source, 'You were blocked tonight.')
            else:
                if check.target.role is not None:
                    rolename = check.target.role.GetRoleName()
                    if rolename == 'Goon' or rolename == 'Civilian':
                        rolename = 'Vanilla'
                    else:
                        rolename = 'a '+rolename
                    self.Send(check.source, 'Your investigation on '+str(check.target)+' reveals him to be '+rolename+'.')
                else:
                    self.Send(check.source, 'Your investigation on '+str(check.target)+' reveals him to not have a role at all. Strange.')

        # handle trackings
        tracks = [action for action in self.actionlist if action.actiontype == MafiaAction.TRACK]
        for track in tracks:
            if track.source in blockset:
                self.Send(track.source, 'You were blocked tonight.')
            else:
                visits = [str(action.target) for action in self.actionlist if (action.source is track.target and action.visiting and (action.actiontype == MafiaAction.BLOCK or action.source not in blockset))]
                if visits:
                    self.Send(track.source, str(track.target)+' visited the following players tonight: '+', '.join(visits))
                else:
                    self.Send(track.source, str(track.target)+' did not visit anybody tonight.')
                    
        # handle watches
        watchs = [action for action in self.actionlist if action.actiontype == MafiaAction.WATCH]
        for watch in watchs:
            if watch.source in blockset:
                self.Send(watch.source, 'You were blocked tonight.')
            else:
                visits = [str(action.source) for action in self.actionlist if (action.target is watch.target and not action.source is watch.source and action.visiting and (action.actiontype == MafiaAction.BLOCK or action.source not in blockset))]
                if visits:
                    self.Send(watch.source, str(watch.target)+' was visited by the following players tonight: '+', '.join(visits))
                else:
                    self.Send(watch.source, str(watch.target)+' was not visited tonight.')

        # handle callback actions
        callbacks = [action for action in self.actionlist if action.actiontype == MafiaAction.CALLBACK]
        for callback in callbacks:
            if callback.source in blockset:
                blocked = True
            else:
                blocked = False
            callback.modifiers['callback'](callback.source, self, blocked)

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
                killstatus, flipmsg = kill.target.Kill(self, True)
                if killstatus:
                    nokills = False
                    self.Send(self.mainchannel, kill.target+flipmsg+' has died tonight!', max_messages=10)
        if nokills:
            self.Send(self.mainchannel, 'Nobody has died tonight!', max_messages=10)
        # reset actionlist
        self.actionlist = []
        # send history to deadchat
        self.Send(self.deadchat, nighthistory, max_messages=10)

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

    def BeginNightPhase(self):
        self.daycount += 1
        self.phase = self.NIGHTPHASE
        self.Send(self.mainchannel, 'Night '+str(self.daycount)+' has started. Go to sleep and take required actions.')
        self.votes = dict()
        for player in self.players.values():
            if not player.IsDead():
                self.votes[player] = (self.NOVOTE, time.clock())
                player.BeginNightPhase(self)
        self.factionkills = self.GetNightKillPower()
        for mafiach in self.mafiachannels:
            self.Send(mafiach, 'You have '+str(self.factionkills)+' kills tonight. Use !kill <target> to use them. The player issuing the command will carry out the kill. Use !nokill to pass on the remaining faction kills for the night.')

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
    def GameLoop(self):
        if self.joinchannels:
            for chn in self.mafiachannels:
                self.JoinChannel(chn)
                self.Action('MODE ', chn+' +s')
            self.JoinChannel(self.deadchat)
            self.JoinChannel(self.mainchannel)
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
                self.HandleActionList()
                if not self.CheckForWinCondition():
                    self.phase = self.DAYPHASE
                    self.time = time.clock()
                    # reset votes
                    self.votes = dict()
                    for player in self.players.values():
                        if not player.IsDead():
                            self.votes[player] = (self.NOVOTE, time.clock())
                    self.Send(self.mainchannel, 'Day '+str(self.daycount)+' has just begun. The Town consists of '+self.GetPlayers())
                else:
                    self.ResetGame()
