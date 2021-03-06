from MafiaBot.MafiaRole import MafiaRole
from MafiaBot.MafiaAction import MafiaAction


class Gunsmith(MafiaRole):

    def GetRolePM(self):
        ret = 'You are a Gunsmith. You may give another player a gun during the night.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName():
        return 'Gunsmith'

    @staticmethod
    def GetRoleDescription():
        return 'Gunsmiths hand out guns to other players at night. These guns can then be used to carry out night kills.'

    def HandleCommand(self, command, param, mb, player):
        if self.requiredaction:
            if command == 'send':
                if not self.limiteduses == 0:
                    target = mb.GetPlayer(param)
                    if target is not None:
                        if not target.IsDead():
                            if target is player:
                                return 'You cannot give a gun to yourself!'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.SENDITEM, player, target, True, {'item': 'gun'}))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You send a gun to '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' guns remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Gunsmith: You may send another player a gun tonight. Use !send <player> to give a gun to that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' guns remaining.'
            return ret
        else:
            return ''
