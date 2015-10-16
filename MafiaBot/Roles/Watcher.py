from MafiaBot.MafiaRole import MafiaRole
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction


class Watcher(MafiaRole):

    def GetRolePM(self):
        ret = 'You are a Watcher. You may hide outside another player\'s house at night and see the players that visit them.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName(self):
        return 'Watcher'

    @staticmethod
    def GetRoleDescription():
        return 'Watchers observe other players\' homes at night. They will receive a report with all the players visiting their target that night. They themselves can be followed to their target.'

    def HandleCommand(self, command, param, bot, mb, player):
        if self.requiredaction:
            if command == 'watch':
                if not self.limiteduses == 0:
                    target = Identifier(param)
                    if target in mb.players:
                        if not mb.players[target].IsDead():
                            if mb.players[target] is player:
                                return 'You cannot watch yourself!'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.WATCH, player.name, target, True))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You watch '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' uses remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player, bot):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Watcher: You may observe another player tonight. Use !watch <player> to take camp outside their house.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' uses remaining.'
            return ret
        else:
            return ''
