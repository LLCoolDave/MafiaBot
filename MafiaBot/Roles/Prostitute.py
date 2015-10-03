from MafiaBot.MafiaRole import MafiaRole
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction


class Prostitute(MafiaRole):

    def __init__(self, settings=dict()):
        super(Prostitute, self).__init__(settings)
        self.lastpick = (None, 0)

    def GetRolePM(self):
        ret = 'You are a Prostitute. You may roleblock another player during the night. You cannot pick the same player on two consecutive nights.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    def GetRoleName(self):
        return 'Prostitute'

    @staticmethod
    def GetRoleDescription():
        return 'Prostitutes are roleblockers, disabling the active abilities of another player at night. Roleblocks do not interfer with each other, but prevent all other actions by the blocked player. A prositute may not pick the same player on two consecutive nights.'

    def HandleCommand(self, command, param, bot, mb, player):
        if self.requiredaction:
            if command == 'block':
                if not self.limiteduses == 0:
                    target = Identifier(param)
                    if self.lastpick[0] is None or self.lastpick[1]+1 < mb.daycount:
                        lastpick = Identifier('')
                    else:
                        lastpick = self.lastpick[0]
                    if target in mb.players:
                        if not mb.players[target].IsDead():
                            if mb.players[target] is player or target == lastpick:
                                return 'You cannot block that player.'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.BLOCK, player.name, target, True))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You block '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                self.lastpick = (target, mb.daycount)
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' blocks remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player, bot):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Prostitute: You may roleblock another player tonight. Use !block <player> to block that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' uses remaining.'
            if self.lastpick[0] is not None and self.lastpick[1]+1 >= mb.daycount:
                ret += ' Your last pick was: '+str(self.lastpick[0])
            return ret
        else:
            return ''
