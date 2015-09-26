__author__ = 'LLCoolDave'

class MafiaRole:

    def __init__(self):
        self.mandatoryaction = False
        self.requiredaction = False

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
