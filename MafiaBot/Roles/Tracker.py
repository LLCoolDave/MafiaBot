from MafiaBot.MafiaRole import MafiaRole
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction


class Tracker(MafiaRole):

    def GetRolePM(self):
        ret = 'You are a Tracker. You may stalk another player at night and see the players they visit.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName(self):
        return 'Tracker'

    @staticmethod
    def GetRoleDescription():
        return 'Trackers follow other players at night. They will receive a report with all the players visited by their target that night. They themselves can be followed to their target.'

    def HandleCommand(self, command, param, bot, mb, player):
        if self.requiredaction:
            if command == 'track':
                if not self.limiteduses == 0:
                    target = Identifier(param)
                    if target in mb.players:
                        if not mb.players[target].IsDead():
                            if mb.players[target] is player:
                                return 'You cannot track yourself!'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.TRACK, player.name, target, True))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You track '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' tracks remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player, bot):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Tracker: You may follow another player tonight. Use !track <player> to track that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' uses remaining.'
            return ret
        else:
            return ''
