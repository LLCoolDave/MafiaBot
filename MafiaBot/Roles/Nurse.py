from MafiaBot.MafiaRole import MafiaRole
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction


class Nurse(MafiaRole):

    def GetRolePM(self):
        ret = 'You are a Nurse. You may give another player a syringe during the night.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName():
        return 'Nurse'

    @staticmethod
    def GetRoleDescription():
        return 'Nurses hand out syringes to other players at night. They can be used to protect any player from a night kill.'

    def HandleCommand(self, command, param, mb, player):
        if self.requiredaction:
            if command == 'send':
                if not self.limiteduses == 0:
                    target = Identifier(param)
                    if target in mb.players:
                        if not mb.players[target].IsDead():
                            if mb.players[target] is player:
                                return 'You cannot give a syringe to yourself!'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.SENDITEM, player.name, target, True, {'item': 'syringe'}))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You send a syringe to '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' syringes remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Nurse: You may send another player a syringe tonight. Use !send <player> to give a syringe to that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' syringes remaining.'
            return ret
        else:
            return ''
