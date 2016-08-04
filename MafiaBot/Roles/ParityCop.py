from MafiaBot.MafiaRole import MafiaRole
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction


class ParityCop(MafiaRole):

    def __init__(self, settings=dict()):
        super(ParityCop, self).__init__(settings)
        self.lastcheck = None
        self.currentcheck = None

    def GetRolePM(self):
        ret = 'You are a Parity Cop. You may check the faction of another player at night. However, you will only learn if the faction is the same or different from your last successful check.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName():
        return 'Parity Cop'

    @staticmethod
    def GetRoleDescription():
        return 'Parity Cops investigate other player\'s faction at night. They will receive a report if their target has the same or a different faction than their last successful check.'

    def HandleCommand(self, command, param, mb, player):
        if self.requiredaction:
            if command == 'check':
                if not self.limiteduses == 0:
                    target = Identifier(param)
                    if target in mb.players:
                        if not mb.players[target].IsDead():
                            if mb.players[target] is player:
                                return 'You cannot investigate yourself!'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.CALLBACK, player.name, target, True, {'callback': self.Callback}))
                                self.requiredaction = False
                                self.currentcheck = target
                                player.UpdateActions()
                                ret = 'You investigate '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' checks remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Parity Cop: You may investigate another player tonight. Use !check <player> to investigate that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' uses remaining.'
            if self.lastcheck is not None:
                ret += ' Your last successful check was on '+str(self.lastcheck)+'.'
            return ret
        else:
            return ''

    def Callback(self, source, mafiabot, blocked):
        if blocked:
            mafiabot.Send(source, 'You were blocked tonight.', max_messages=10)
        else:
            if self.lastcheck is None:
                mafiabot.Send(source, 'You investigated '+str(self.currentcheck)+' tonight. Now if you only had something to compare the results with.', max_messages=10)
            else:
                lastfaction = mafiabot.players[self.lastcheck].GetFaction()
                currentfaction = mafiabot.players[self.currentcheck].GetFaction()
                if lastfaction == currentfaction:
                    reply = 'the same faction.'
                else:
                    reply = 'different factions.'
                mafiabot.Send(source, 'Your investigations show that '+str(self.lastcheck)+' and '+str(self.currentcheck)+' belong to ' + reply, max_messages=10)
            self.lastcheck = self.currentcheck
