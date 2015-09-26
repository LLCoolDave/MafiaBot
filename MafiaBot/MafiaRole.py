__author__ = 'LLCoolDave'


class MafiaRole(object):

    def __init__(self, settings=dict()):
        self.mandatoryaction = False
        self.requiredaction = False
        if 'limiteduses' in settings:
            self.limiteduses = settings['limiteduses']
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
