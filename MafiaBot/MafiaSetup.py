from MafiaPlayer import MafiaPlayer
from Roles.rolelist import Roles

def Basic7(playercount):
    rolelist = [(MafiaPlayer.FACTION_MAFIA, 'goon', dict()),
            (MafiaPlayer.FACTION_MAFIA, 'prostitute', dict()),
            (MafiaPlayer.FACTION_TOWN, 'cop', {'limiteduses': 1}),
            (MafiaPlayer.FACTION_TOWN, 'medic', dict()),
            (MafiaPlayer.FACTION_TOWN, 'civilian', dict()),
            (MafiaPlayer.FACTION_TOWN, 'civilian', dict()),
            (MafiaPlayer.FACTION_TOWN, 'civilian', dict())]
    return rolelist

class MafiaSetup(object):

    # template: 'shortname': ('setup name', required_players #None to use value from self.requiredplayers, 'Setup description', function(playercount) #returns rolelist)
    PREDEFINED = {'basic7': ('Basic 7', 7, '1 Mafia Goon, 1 Mafia Prostitute, 1 One-Shot Cop, 1 Medic, 3 Civilians', Basic7)}

    def __init__(self):
        self.requiredplayers = 0
        self.predefined = False
        self.predefinedName = ''
        self.rolelist = []
        self.closed = False
        self.admin = None
        self.daystart = False

    def GetRequiredPlayers(self):
        return self.requiredplayers

    def GetDaystart(self):
        return self.daystart

    def HandleCommand(self, nick, rawcommand, mafiabot):
        if rawcommand is not None:
            params = rawcommand.split()
        else:
            params = None
        retstr = None
        if not params:
            # plain !setup command was issued, return information on the setup
            retstr = self.GetSetupDescription(nick, mafiabot)
        elif (not self.closed) or self.admin == nick:
            if params[0] == 'load':
                retstr = self.LoadPredefinedSetup(params[1:], mafiabot)
            elif params[0] == 'closed':
                self.closed = True
                self.admin = nick
                retstr = "Setup is now closed. Only you may modify and look at it further."
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
        if not params[1] in Roles:
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
        self.rolelist.append((faction, params[1], settings))
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
        #ToDo better display
        if role[0] == MafiaPlayer.FACTION_MAFIA:
            factionstr = 'Mafia'
        elif role[0] == MafiaPlayer.FACTION_TOWN:
            factionstr = 'Town'
        else:
            factionstr = ''
        return factionstr+' '+role[1]+' '+str(role[2])

    def LoadPredefinedSetup(self, params, mafiabot):
        if not params:
            return 'This command requires one parameter. Expected format: !setup load <setup short name>.'
        elif not params[0] in self.PREDEFINED:
            return 'I do not know the setup '+params[0]
        self.predefined = True
        self.predefinedName = params[0]
        setup = self.PREDEFINED[params[0]]
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
        retstr = 'This is '+closedstr+' '+daystartstr+' setup for '+str(self.requiredplayers)+' players. It features the following roles:'
        i = 0
        for role in self.rolelist:
            retstr += ' '+str(i) + ': '+self._RoleToString(role)
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
        return rolelist