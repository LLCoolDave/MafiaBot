from MafiaBot.MafiaRole import MafiaRole
from MafiaBot.MafiaAction import MafiaAction


class Armorsmith(MafiaRole):

    def GetRolePM(self):
        ret = 'You are an Armorsmith. You may give another player a bulletproof vest during the night.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName():
        return 'Armorsmith'

    @staticmethod
    def GetRoleDescription():
        return 'Armorsmiths hand out bulletproof vests to other players at night. These vests protect their owner from a night kills.'

    def HandleCommand(self, command, param,  mb, player):
        if self.requiredaction:
            if command == 'send':
                if not self.limiteduses == 0:
                    target = mb.GetPlayer(param)
                    if target is not None:
                        if not target.IsDead():
                            if target is player:
                                return 'You cannot give a vest to yourself!'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.SENDITEM, player, target, True, {'item': 'vest'}))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You send a bulletproof vest to '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' vests remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Armorsmith: You may send another player a bulletproof vest tonight. Use !send <player> to give a vest to that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' vest remaining.'
            return ret
        else:
            return ''
