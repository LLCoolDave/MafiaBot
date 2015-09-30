from Roles.rolelist import Roles
from MafiaPlayer import MafiaPlayer

class MafiaSetup(object):

    def __init__(self):
        self.requiredplayers = 0

    def GetRequiredPlayers(self):
        return self.requiredplayers

    def HandleCommand(self, rawcommand, mafiabot):
        return None

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