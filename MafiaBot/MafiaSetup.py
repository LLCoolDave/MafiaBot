from .MafiaPlayer import MafiaPlayer
from .Roles.rolelist import Roles
import random


def Basic7(playercount):
    rolelist = [(MafiaPlayer.FACTION_MAFIA, 'goon', dict()),
                (MafiaPlayer.FACTION_MAFIA, 'prostitute', dict()),
                (MafiaPlayer.FACTION_TOWN, 'cop', {'limiteduses': 1}),
                (MafiaPlayer.FACTION_TOWN, 'medic', dict()),
                (MafiaPlayer.FACTION_TOWN, 'civilian', dict()),
                (MafiaPlayer.FACTION_TOWN, 'civilian', dict()),
                (MafiaPlayer.FACTION_TOWN, 'civilian', dict())]
    return rolelist


def Test(playercount):
    rolelist = [(MafiaPlayer.FACTION_MAFIA, 'goon', dict()),
                (MafiaPlayer.FACTION_MAFIA, 'prostitute', dict()),
                (MafiaPlayer.FACTION_TOWN, 'cop', {'limiteduses': 1}),
                (MafiaPlayer.FACTION_TOWN, 'bulletproof', dict()),
                (MafiaPlayer.FACTION_TOWN, 'gunsmith', {'limiteduses': 1}),
                (MafiaPlayer.FACTION_TOWN, 'vigilante', dict()),
                (MafiaPlayer.FACTION_TOWN, 'paritycop', dict())]
    return rolelist


def C9(playercount):
    rolelist = [(MafiaPlayer.FACTION_MAFIA, 'goon', dict()),
                (MafiaPlayer.FACTION_MAFIA, 'goon', dict()),
                (MafiaPlayer.FACTION_TOWN, 'civilian', dict()),
                (MafiaPlayer.FACTION_TOWN, 'civilian', dict()),
                (MafiaPlayer.FACTION_TOWN, 'civilian', dict())]
    rnd = random.randint(1, 4)
    if rnd == 1:
        rolelist.append((MafiaPlayer.FACTION_TOWN, 'cop', dict()))
        rolelist.append((MafiaPlayer.FACTION_TOWN, 'medic', dict()))
    elif rnd == 2:
        rolelist.append((MafiaPlayer.FACTION_TOWN, 'cop', dict()))
        rolelist.append((MafiaPlayer.FACTION_TOWN, 'civilian', dict()))
    elif rnd == 3:
        rolelist.append((MafiaPlayer.FACTION_TOWN, 'civilian', dict()))
        rolelist.append((MafiaPlayer.FACTION_TOWN, 'medic', dict()))
    elif rnd == 4:
        rolelist.append((MafiaPlayer.FACTION_TOWN, 'civilian', dict()))
        rolelist.append((MafiaPlayer.FACTION_TOWN, 'civilian', dict()))
    return rolelist


class MafiaSetup(object):

    # template: 'shortname': ('setup name', required_players #None to use value from self.requiredplayers, 'Setup description', function(playercount) #returns rolelist)
    PREDEFINED = {'basic7': ('Basic 7', 7, '1 Mafia Goon, 1 Mafia Prostitute, 1 One-Shot Cop, 1 Medic, 3 Civilians', Basic7),
                  'c9': ('C9', 7, 'http://wiki.mafiascum.net/index.php?title=C9', C9),
                  'test': ('Test', 7, 'Only for bot module test. Not intended for actual play.', Test)}

    REDUCTION_MAFIA = 0
    REDUCTION_PLAYERS = 1

    def __init__(self):
        self.requiredplayers = None
        self.predefined = False
        self.predefinedName = ''
        self.rolelist = []
        self.closed = False
        self.admin = None
        self.daystart = False
        self.revealfaction = True
        self.revealrole = True
        self.mafiakillpower = 1
        self.killpowerreduction = None

    def GetRequiredPlayers(self):
        return self.requiredplayers

    def GetDaystart(self):
        return self.daystart

    def HandleCommand(self, nick, rawcommand, mafiabot):
        if rawcommand is not None:
            params = rawcommand.lower().split()
        else:
            params = None
        retstr = None
        if not params:
            # plain !setup command was issued, return information on the setup
            retstr = self.GetSetupDescription(nick, mafiabot)
        elif (not mafiabot.active) and ((not self.closed) or self.admin == nick):
            if params[0] == 'load':
                retstr = self.LoadPredefinedSetup(params[1:], mafiabot)
            elif params[0] == 'closed':
                self.closed = True
                self.admin = nick
                retstr = "Setup is now closed. Only you may modify and look at it further."
            elif params[0] == 'reveal':
                if len(params) > 1:
                    if params[1] == 'role':
                        self.revealrole = True
                        retstr = "Roles are now revealed on death."
                    elif params[1] == 'faction':
                        self.revealfaction = True
                        retstr = "Factions are now revealed on death."
            elif params[0] == 'hide':
                if len(params) > 1:
                    if params[1] == 'role':
                        self.revealrole = False
                        retstr = "Roles are now hidden on death."
                    elif params[1] == 'faction':
                        self.revealfaction = False
                        retstr = "Factions are now hidden on death."
            elif params[0] == 'open':
                self.closed = False
                self.admin = None
                retstr = "Setup is now open."
            elif params[0] == 'daystart':
                self.daystart = True
                retstr = "This game will start at day 0."
            elif params[0] == 'nightstart':
                self.daystart = False
                retstr = "This game will start at night 1."
            elif params[0] == 'unload':
                self.predefined = False
                self.requiredplayers = len(self.rolelist) if self.rolelist else None
                retstr = "Unloaded predefined setup."
            elif params[0] == 'playercount':
                if self.predefined:
                    if self.PREDEFINED[self.predefinedName][1] is None:
                        try:
                            playercount = int(params[1])
                            self.requiredplayers = playercount
                            return 'Set required players to '+str(playercount)
                        except:
                            pass
            elif params[0] == 'add':
                if not self.predefined:
                    retstr = self.AddRole(params[1:], mafiabot)
            elif params[0] == 'modify':
                if not self.predefined:
                    retstr = self.ModifyRole(params[1:], mafiabot)
            elif params[0] == 'drop':
                if not self.predefined:
                    retstr = self.DropRole(params[1:], mafiabot)
            elif params[0] == 'killpower':
                if not self.predefined:
                    try:
                        self.mafiakillpower = int(params[1])
                        retstr = 'Mafia night kill power set to %u.' % self.mafiakillpower
                    except:
                        pass
            elif params[0] == 'killpowerreduction':
                if not self.predefined:
                    if params[1] == 'mafia':
                        try:
                            self.killpowerreduction = (self.REDUCTION_MAFIA, int(params[2]))
                            retstr = 'Killpower will be reduced to 1 once there is %u or less Mafia left in the game.'
                        except:
                            pass
                    elif params[1] == 'players':
                        try:
                            self.killpowerreduction = (self.REDUCTION_PLAYERS, int(params[2]))
                            retstr = 'Killpower will be reduced to 1 once there is %u or less Players left in the game.'
                        except:
                            pass
        return retstr

    def AddRole(self, params, mafiabot):
        if len(params) < 2:
            return 'This command requires at least two parameters. Expected format: !setup add <faction> <rolename> [<numberofuses> [<additional parameters in form name=value>]]'
        if params[0].lower() == 'mafia':
            faction = MafiaPlayer.FACTION_MAFIA
        elif params[0].lower() == 'town':
            faction = MafiaPlayer.FACTION_TOWN
        else:
            return 'I do not know the faction '+params[0]
        if not params[1].lower() in Roles:
            return 'I do not know the role '+params[1]
        retstr = 'Added '+params[0]+' '+params[1]
        settings = dict()
        if len(params) > 2:
            try:
                uses = int(params[2])
            except:
                uses = -1
            settings['limiteduses'] = uses
            retstr += ' with '+str(uses)+' uses'
        retstr += ' with additional parameters:'
        for param in params[3:]:
            split = param.split('=')
            if len(split) == 2:
                settings[split[0]] = split[1]
                retstr += ' '+param
        self.rolelist.append((faction, params[1].lower(), settings))
        if self.requiredplayers is None:
            self.requiredplayers = 1
        else:
            self.requiredplayers += 1
        return retstr

    def ModifyRole(self, params, mafiabot):
        return 'This command is currently not implemented. Please use drop and add for now.'

    def DropRole(self, params, mafiabot):
        if len(params) < 1:
            return 'This command requires one parameter. Expected format: !setup drop <index>. The index corresponds to the numbers listed in the blank !setup command.'
        try:
            role = self.rolelist.pop(int(params[0]))
            self.requiredplayers -= 1
            return 'Removed '+self._RoleToString(role)+' at index '+params[0]+'. All following indices shift down by one.'
        except:
            return 'Could not remove role with index '+params[0]+'. This is either not a number or this index does not exist currently.'

    def _RoleToString(self, role):
        # ToDo better display
        if role[0] == MafiaPlayer.FACTION_MAFIA:
            factionstr = 'Mafia'
        elif role[0] == MafiaPlayer.FACTION_TOWN:
            factionstr = 'Town'
        else:
            factionstr = ''
        if role[2]:
            settingsstr = ' '+str(role[2])
        else:
            settingsstr = ''
        return factionstr+' '+Roles[role[1].lower()].GetRoleName()+settingsstr

    def LoadPredefinedSetup(self, params, mafiabot):
        if not params:
            return 'This command requires one parameter. Expected format: !setup load <setup short name>.'
        elif not params[0] in self.PREDEFINED:
            return 'I do not know the setup '+params[0]
        self.predefined = True
        self.predefinedName = params[0]
        setup = self.PREDEFINED[params[0]]
        self.requiredplayers = setup[1] if setup[1] is not None else 0
        return 'Loaded setup '+setup[0]+': '+setup[2]

    def GetSetupDescription(self, nick, mafiabot):
        if self.closed and (not self.admin == nick):
            return 'This setup is closed and administrated by '+str(self.admin)+'. You do not get any information about it.'
        if self.predefined:
            setup = self.PREDEFINED[self.predefinedName]
            if setup[1] is None:
                playercount = self.requiredplayers
            else:
                playercount = int(setup[1])
            return 'This is the predefined setup '+setup[0]+' for '+str(playercount)+' players. Short description: '+setup[2]
        if self.daystart:
            daystartstr = 'day-start'
        else:
            daystartstr = 'night-start'
        if self.closed:
            closedstr = 'a closed'
        else:
            closedstr = 'an open'
        killpowerreductionstr = ''
        if self.killpowerreduction is not None:
            if self.killpowerreduction[0] == self.REDUCTION_MAFIA:
                killpowerreductionstr = ' until only %u Mafia are left.' % self.killpowerreduction[1]
            elif self.killpowerreduction[0] == self.REDUCTION_PLAYERS:
                killpowerreductionstr = ' until only %u Players are left.' % self.killpowerreduction[1]
        killpowerstr = 'Mafia has %u night kill power%s.' % (self.mafiakillpower, killpowerreductionstr)
        retstr = 'This is '+closedstr+' '+daystartstr+' setup for '+str(self.requiredplayers)+' players. '+killpowerstr+' It features the following roles:'
        i = 0
        for role in self.rolelist:
            retstr += ' \x02'+str(i) + '\x02: '+self._RoleToString(role)
            i += 1
        return retstr

    def GetRoleList(self, mb):
        if self.predefined:
            setup = self.PREDEFINED[self.predefinedName]
            if setup[1] is None:
                playercount = self.requiredplayers
            else:
                playercount = int(setup[1])
            rolelist = setup[3](playercount)
        else:
            rolelist = self.rolelist
        return list(rolelist)
