from MafiaPlayer import MafiaPlayer

class MafiaSetup(object):

    def __init__(self):
        self.requiredplayers = 0
        self.predefined = False
        self.predefinedNamed = ''

    def GetRequiredPlayers(self):
        return self.requiredplayers

    def HandleCommand(self, rawcommand, mafiabot):
        params = rawcommand.split()
        retstr = None
        if not params:
            # plain !setup command was issues, return information on the setup
            retstr = self.GetSetupDescription(mafiabot)
        elif params[0] == 'load':
            retstr = self.LoadPredefinedSetup(params[1:], mafiabot)
        elif params[0] == 'unload':
            self.predefined = False
            retstr = "Unloaded predefined setup."
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
        return None

    def ModifyRole(self, params, mafiabot):
        return None

    def DropRole(self, params, mafiabot):
        return None

    def LoadPredefinedSetup(self, params, mafiabot):
        return None

    def GetSetupDescription(self, mafiabot):
        return 'Not implemented yet.'

    def GetRoleList(self, mb):
        playercount = len(mb.players)
        mafiacount = (playercount / 5) + 1  # 20% mafia for the start
        if playercount == 7:
            # use the basic setup
            mafiacount = 2
            rolelist = [(MafiaPlayer.FACTION_MAFIA, 'goon', dict()),
                        (MafiaPlayer.FACTION_MAFIA, 'prostitute', dict()),
                        (MafiaPlayer.FACTION_TOWN, 'cop', dict()),
                        (MafiaPlayer.FACTION_TOWN, 'medic', dict()),
                        (MafiaPlayer.FACTION_TOWN, 'civilian', dict()),
                        (MafiaPlayer.FACTION_TOWN, 'civilian', dict()),
                        (MafiaPlayer.FACTION_TOWN, 'civilian', dict())]
        else:
            rolelist = [(MafiaPlayer.FACTION_MAFIA, 'goon', dict())]*mafiacount + [(MafiaPlayer.FACTION_TOWN, 'civilian', dict())]*(playercount-mafiacount)

        return rolelist