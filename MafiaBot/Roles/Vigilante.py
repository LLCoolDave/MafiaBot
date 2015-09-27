from MafiaBot.MafiaRole import MafiaRole
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction

class Vigilante(MafiaRole):

    def GetRolePM(self):
        ret = 'You are a Vigilante. You may pick and kill people at your will during the night.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    def GetRoleName(self):
        return 'Vigilante'

    @staticmethod
    def GetRoleDescription():
        return 'Vigilantes execute judgement on their own account. During the night, a vigilante may shoot his gun to kill another player.'

    def HandleCommand(self, command, param, bot, mb, player):
        if self.requiredaction:
            if command == 'shoot':
                if not self.limiteduses == 0:
                    target = Identifier(param)
                    if target in mb.players:
                        if not mb.players[target].IsDead():
                            if mb.players[target] is player:
                                return 'You cannot shoot yourself!'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.KILL, player.name, target, True))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You will shoot '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                if self.limiteduses > -1:
                                    ret += 'You have '+str(self.limiteduses)+' bullets remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player, bot):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Vigilante: You may shoot another player tonight. Use !shoot <player> to kill that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' uses remaining.'
            return ret
        else:
            return ''

    def NightKillPower(self):
        if self.limiteduses == 0:
            return 0
        else:
            return 1
