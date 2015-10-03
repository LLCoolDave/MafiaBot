from MafiaBot.MafiaRole import MafiaRole
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction


class Cop(MafiaRole):

    def __init__(self, settings=dict()):
        super(Cop, self).__init__(settings)
        if 'sanity' in settings:
            self.sanity = settings['sanity']
        else:
            self.sanity = 'sane'

    def GetRolePM(self):
        ret = 'You are a Cop. You may check the alignment of another player at night.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    def GetRoleName(self):
        return 'Cop'

    @staticmethod
    def GetRoleDescription():
        return 'Cops investigate other players at night. They will receive a report with that players faction alignment at the end of the night.'

    def HandleCommand(self, command, param, bot, mb, player):
        if self.requiredaction:
            if command == 'check':
                if not self.limiteduses == 0:
                    target = Identifier(param)
                    if target in mb.players:
                        if not mb.players[target].IsDead():
                            if mb.players[target] is player:
                                return 'You cannot investigate yourself!'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.CHECKFACTION, player.name, target, True, {'sanity': self.sanity}))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You investigate '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' checks remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player, bot):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Cop: You may check another player\'s alignment tonight. Use !check <player> to investigate that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' uses remaining.'
            return ret
        else:
            return ''
