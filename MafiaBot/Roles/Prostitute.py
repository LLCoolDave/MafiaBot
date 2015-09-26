from MafiaBot.MafiaRole import MafiaRole
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction

class Prostitute(MafiaRole):

    def GetRolePM(self):
        ret = 'You are a Prostitute. You may roleblock another player during the night.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    def GetRoleName(self):
        return 'Prostitute'

    @staticmethod
    def GetRoleDescription():
        return 'Prostitutes are roleblockers, disabling the active abilities of another player at night. Roleblocks do not interfer with each other, but prevent all other actions by the blocked player.'

    def HandleCommand(self, command, param, bot, mb, player):
        if self.requiredaction:
            if command == 'block':
                if not self.limiteduses == 0:
                    target = Identifier(param)
                    if target in mb.players:
                        if not mb.players[target].IsDead():
                            if mb.players[target] is player:
                                return 'You cannot block that player.'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.BLOCK, player.name, target, True))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You block '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                if self.limiteduses > -1:
                                    ret += 'You have '+str(self.limiteduses)+' blocks remaining.'
                                return ret
                    return 'Cannot find player '+param
                else:
                    return 'You have no uses left.'
        return None

    def BeginNightPhase(self, mb, player, bot):
        self.requiredaction = True
        ret = 'Prostitute: You may roleblock another player tonight. Use !block <player> to block that player.'
        if self.limiteduses > -1:
            ret += ' You have '+str(self.limiteduses)+' uses remaining.'
        return ret
