from MafiaBot.MafiaRole import MafiaRole
from MafiaBot.MafiaAction import MafiaAction


class Sleepwalker(MafiaRole):

    def GetRolePM(self):
        ret = 'You are a Sleepwalker. You have to visit another player at night. This action does nothing.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName():
        return 'Sleepwalker'

    @staticmethod
    def GetRoleDescription():
        return 'Sleepwalkers compulsorily visit other players at night. That action accomplishes nothing.'

    def HandleCommand(self, command, param, mb, player):
        if self.requiredaction:
            if command == 'visit':
                if not self.limiteduses == 0:
                    target = mb.GetPlayer(param)
                    if target is not None:
                        if not target.IsDead():
                            if target is player:
                                return 'You cannot visit yourself!'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.VISIT, player, target, True))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You visit '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' visits remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player):
        if not self.limiteduses == 0:
            self.requiredaction = True
            self.mandatoryaction = True
            ret = 'Sleepwalker: [Mandatory!] You have to visit another player tonight. Use !visit <player> to visit that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' visits remaining.'
            return ret
        else:
            return ''
