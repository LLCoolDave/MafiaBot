from MafiaBot.MafiaRole import MafiaRole
from MafiaBot.MafiaAction import MafiaAction


class CorruptBureaucrat(MafiaRole):

    def GetRolePM(self):
        ret = 'You are a Corrupt Bureaucrat. You may receive a list of all roles alive going into the night.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    def GetRoleName(self):
        return 'Corrupt Bureaucrat'

    @staticmethod
    def GetRoleDescription():
        return 'Corrupt Bureaucrat can request a list of all active roles going into a night.'

    def HandleCommand(self, command, param, bot, mb, player):
        if self.requiredaction:
            if command == 'check':
                if not self.limiteduses == 0:
                    mb.actionlist.append(MafiaAction(MafiaAction.CORRUPTBUREAUCRAT, None, None, False))
                    self.requiredaction = False
                    player.UpdateActions()
                    ret = 'You choose to use your power tonight.'
                    self.limiteduses -= 1
                    if self.limiteduses > -1:
                        ret += 'You have '+str(self.limiteduses)+' uses remaining.'
                    return ret
        return None

    def BeginNightPhase(self, mb, player, bot):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Corrupt Bureaucrat: You may request a list of all active roles tonight. Use !check to use your power.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' uses remaining.'
            return ret
        else:
            return ''
