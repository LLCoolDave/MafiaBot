from ResistancePlayer import ResistancePlayer
from sopel.tools import Identifier
import random


class ResistanceBot:

    FACTIONCOUNT = {5: (3, 2),
                    6: (4, 2),
                    7: (4, 3),
                    8: (5, 3),
                    9: (6, 3),
                    10: (6, 4)}

    MISSIONSETUP = {5: (2, 3, 2, 3, 3),
                    6: (2, 3, 4, 3, 4),
                    7: (2, 3, 3, 4, 4),
                    8: (3, 4, 4, 5, 5),
                    9: (3, 4, 4, 5, 5),
                    10: (3, 4, 4, 5, 5)}

    NEWLEADERPHASE = 0
    SELECTTEAMPHASE = 1
    PRETEAMVOTEPHASE = 2
    TEAMVOTEPHASE = 3
    PREMISSIONPHASE = 4
    MISSIONPHASE = 5
    POSTMISSIONPHASE = 6

    def __init__(self):
        self.channel = '#fridaynightmafia'
        self._ResetGame()

    def _ResetGame(self):
        self.active = False
        self.players = {}
        self.mission = None
        self.votecount = None
        self.leader = None
        self.playerorder = []
        self.teamvote = {}
        self.missionvote = {}
        self.team = []
        self.mission_required = None
        self.phase = None
        self.failedrequired = None
        self.missionresults = []

    def __getitem__(self, item):
        try:
            return self.players[item]
        except:
            return None

    def __setitem__(self, key, value):
        self.players[key] = value

    def HandleCommand(self, command, source, nick, param, bot):
        if param is not None:
            param = param.rstrip()
        if command == 'abort':
            self._ResetGame()
            return 'Reset ongoing Resistance game!'
        elif command == 'join':
            if not self.active and nick not in self.players and len(self.players) < 10:
                self[nick] = ResistancePlayer(nick)
                bot.msg(self.channel, nick + ' has joined the game. There are currently '+str(len(self.players))+' Players in the game.')
            return None
        elif command == 'drop':
            if not self.active and nick in self.players:
                del self.players[nick]
                bot.msg(self.channel, nick + ' has dropped from the game. There are currently '+str(len(self.players))+' Players in the game.')
            return None
        elif command == 'start':
            if not self.active:
                return self.StartGame(bot)
            return None
        elif command == 'team':
            if self.phase == self.SELECTTEAMPHASE:
                if nick == self.leader:
                    nicks = param.split()
                    toadd = []
                    for player in nicks:
                        p = Identifier(player)
                        if p in self.players and p not in self.team and p not in toadd:
                            toadd.append(self.players[p].nick)
                    if len(self.team) + len(toadd) > self.mission_required:
                        return 'You specified more team members than required for this mission. Please try again.'
                    else:
                        self.team.extend(toadd)
                        if len(self.team) == self.mission_required:
                            return self.VoteTeam()
                        else:
                            return 'The team currently consists of: %s  You need to add %s more members.' % (', '.join(self.team), self.mission_required - len(self.team))
        elif command == 'teamvote':
            if self.phase == self.TEAMVOTEPHASE:
                if nick in self.players and nick not in self.teamvote:
                    if param == 'yes':
                        self.teamvote[nick] = True
                    elif param == 'no':
                        self.teamvote[nick] = False
                    # everybody voted
                    if len(self.teamvote) == len(self.players):
                        self.EvaluateTeamVote(bot)
                    return 'Team vote recognized.'
            return None
        elif command == 'missionvote':
            if self.phase == self.MISSIONPHASE:
                if nick in self.players and nick in self.team and nick not in self.missionvote:
                    if param == 'success':
                        self.missionvote[nick] = True
                    elif param == 'fail':
                        if self.players[nick].faction == ResistancePlayer.FACTION_SPIES:
                            self.missionvote[nick] = False
                        else:
                            return 'You are a Resistance member, you cannot vote to fail missions!'
                    # everybody voted
                    if len(self.missionvote) == len(self.team):
                        self.EvaluateMissionVote(bot)
                    return 'Mission vote recognized.'
            return None
        elif command == 'playerorder' or command == 'order':
            if self.active:
                returnstrings = []
                for player in self.playerorder:
                    if player == self.leader:
                        returnstrings.append('\x02%s\x02' % player)
                    else:
                        returnstrings.append(player)
                return 'The player order this game is: %s' % ', '.join(returnstrings)
        return None

    def StartGame(self, bot):
        playercount = len(self.players)
        if playercount < 5:
            return 'There are currently less than the required 5 players signed up.'
        elif playercount > 10:
            return 'There are currently more than the allowed 10 players signed up.'
        self.playerorder = list(self.players.keys())
        random.shuffle(self.playerorder)
        resistancecnt = self.FACTIONCOUNT[playercount][0]
        i = 0
        spies = []
        for player in self.playerorder:
            if i < resistancecnt:
                self.players[player].faction = ResistancePlayer.FACTION_RESISTANCE
            else:
                self.players[player].faction = ResistancePlayer.FACTION_SPIES
                spies.append(player)
            i += 1
        random.shuffle(self.playerorder)
        # send faction PMs
        for player in self.playerorder:
            if self.players[player].faction == ResistancePlayer.FACTION_RESISTANCE:
                bot.msg(player, 'You are a member of the Resistance this game.')
            else:
                bot.msg(player, 'You are a spy this game. The spies are: %s' % ', '.join(spies))
        self.active = True
        self.mission = 0
        self.leader = self.playerorder[random.randint(0, playercount - 1)]
        # send start of game info
        bot.msg(self.channel, 'There are %s players this game. There are %s Resistance members and %s spies. Missions will require %s, %s, %s, %s, and %s players.' % (playercount, self.FACTIONCOUNT[playercount][0], self.FACTIONCOUNT[playercount][1], self.MISSIONSETUP[playercount][0], self.MISSIONSETUP[playercount][1], self.MISSIONSETUP[playercount][2], self.MISSIONSETUP[playercount][3], self.MISSIONSETUP[playercount][4]), max_messages=10)
        bot.msg(self.channel, 'The player order this game is: %s' % ', '.join(self.playerorder), max_messages=10)
        self.NextMission(bot)
        return None

    def EvaluateTeamVote(self, bot):
        votestrings = []
        positive = 0
        negative = 0
        for player in self.playerorder:
            votestring = '\x02' + player+ '\x02: '
            if self.teamvote[player]:
                positive += 1
                votestring += 'Yes'
            else:
                negative += 1
                votestring += 'No'
            votestrings.append(votestring)
        bot.msg(self.channel, 'Votes on team %s proposed by %s: %s' % (', '.join(self.team), self.leader, ' - '.join(votestrings)), max_messages=10)
        if positive >= negative:
            self.StartMission(bot)
        else:
            self.votecount += 1
            if self.votecount >= 5:
                self.EndGame('Spies Vote', bot)
            else:
                self.PassLeader()
                self.team = []
                self.teamvote = {}
                self.phase = self.SELECTTEAMPHASE
                bot.msg(self.channel, 'The new leader is %s. There have been %s unsuccessful teams proposed on mission %s so far.' % (self.leader, self.votecount, self.mission), max_messages=10)

    def EvaluateMissionVote(self, bot):
        positive = 0
        negative = 0
        for player in self.team:
            if self.missionvote[player]:
                positive += 1
            else:
                negative += 1
        if negative >= self.failedrequired:
            missionresult = False
            resultstring = 'The mission failed!'
        else:
            missionresult = True
            resultstring = 'The mission was a success!'
        self.missionresults.append(missionresult)
        bot.msg(self.channel, 'The mission results are in. There were %s SUCCESS and %s FAIL votes. %s' % (positive, negative, resultstring), max_messages=10)
        self.CheckGameEnd(bot)
        if self.active:
            self.NextMission(bot)

    def VoteTeam(self):
        self.teamvote = {}
        self.phase = self.TEAMVOTEPHASE
        return '%s proposed a team of %s for mission %s. Please vote on this team by sending a private msg with !teamvote yes or !teamvote no.' % (self.leader, ', '.join(self.team), self.mission)

    def StartMission(self, bot):
        self.phase = self.MISSIONPHASE
        bot.msg(self.channel, 'The team %s is going on mission %s. The mission will fail if %s or more failed results are submitted. If you are on the team, private msg !missionvote success or !missionvote fail to submit your vote.' % (', '.join(self.team), self.mission, self.failedrequired), max_messages=10)

    def EndGame(self, verdict, bot):
        resistance = []
        spies = []
        for player in self.playerorder:
            if self.players[player].faction == ResistancePlayer.FACTION_RESISTANCE:
                resistance.append(player)
            else:
                spies.append(player)
        if verdict == 'Spies Vote':
            bot.msg(self.channel, 'The Resistance is torn apart by being unable to decide on their mission teams. The Spies this game were: %s.' % ', '.join(spies))
        elif verdict == 'Spies Mission':
            bot.msg(self.channel, 'The Resistance could not identify the spies among their ranks in time. The Spies this game were: %s.' % ', '.join(spies))
        elif verdict == 'Resistance Mission':
            bot.msg(self.channel, 'The Resistance is successful in overthrowing the government. The Resistance this game were: %s.' % ', '.join(resistance))

        self._ResetGame()

    def CheckGameEnd(self, bot):
        # check mission results to see if game ended
        positive = 0
        negative = 0
        for mission in self.missionresults:
            if mission:
                positive += 1
            else:
                negative += 1
        if positive >= 3:
            self.EndGame('Resistance Mission', bot)
        elif negative >= 3:
            self.EndGame('Spies Mission', bot)

    def NextMission(self, bot):
        self.PassLeader()
        self.team = []
        self.teamvote = {}
        self.missionvote = {}
        self.phase = self.SELECTTEAMPHASE
        self.votecount = 0
        self.mission += 1
        self.mission_required = self.MISSIONSETUP[len(self.players)][self.mission - 1]
        if self.mission == 4 and len(self.players) >= 7:
            self.failedrequired = 2
        else:
            self.failedrequired = 1
        bot.msg(self.channel, 'Mission %s has begun. The current leader is \x02%s\x02. You have to pick %s players to send on this mission. The mission will fail if %s or more FAIL votes are submitted.' % (self.mission, self.leader, self.mission_required, self.failedrequired), max_messages=10)

    def PassLeader(self):
        # get current leader index
        leaderindex = 0
        for i in xrange(len(self.playerorder)):
            if self.playerorder[i] == self.leader:
                leaderindex = i
                break

        # move forward
        leaderindex = (leaderindex + 1) % len(self.playerorder)
        # select new leader
        self.leader = self.playerorder[leaderindex]
