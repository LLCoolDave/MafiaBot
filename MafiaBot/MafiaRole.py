__author__ = 'LLCoolDave'


class MafiaRole(object):

    def __init__(self, settings=dict()):
        self.mandatoryaction = False
        self.requiredaction = False
        self.preventtownvictory = False
        if 'limiteduses' in settings:
            self.limiteduses = int(settings['limiteduses'])
        else:
            self.limiteduses = -1

    def GetRolePM(self):
        return ''

    def GetRoleName(self):
        return ''

    @staticmethod
    def GetRoleDescription():
        return 'There is currently no description for this role.'

    def HandleCommand(self, command, param, bot, mb, player):
        return None

    def BeginNightPhase(self, mb, player, bot):
        return ''

    def NightKillPower(self):
        return 0

    def Kill(self, bot, mafiabot):
        pass

    def StartGame(self, bot, player, mafiabot):
        pass

    def CheckSpecialWinCondition(self, mb):
        return False

    def SpecialWin(self, winner, mb, bot):
        pass
