from MafiaBot.MafiaRole import MafiaRole
from MafiaBot.MafiaAction import MafiaAction


class Medic(MafiaRole):

    def __init__(self, settings=dict()):
        super(Medic, self).__init__(settings)
        self.lastpick = (None, 0)

    def GetRolePM(self):
        ret = 'You are a Medic. You may protect a player from one kill during the night. You cannot pick the same player on two consecutive nights.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName():
        return 'Medic'

    @staticmethod
    def GetRoleDescription():
        return 'Medics protect players from night kills. A medic may protect himself, but he may not pick the same player on two consecutive nights.'

    def HandleCommand(self, command, param, mb, player):
        if self.requiredaction:
            if command == 'protect':
                if not self.limiteduses == 0:
                    target = mb.GetPlayer(param)
                    if self.lastpick[0] is None or self.lastpick[1]+1 < mb.daycount:
                        lastpick = None
                    else:
                        lastpick = self.lastpick[0]
                    if target is not None:
                        if not target.IsDead():
                            if target is lastpick:
                                return 'You cannot protect that player.'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.PROTECT, player, target, True))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You protect '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                self.lastpick = (target, mb.daycount)
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' protections remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Medic: You may protect a player tonight. Use !protect <player> to protect that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' uses remaining.'
            if self.lastpick[0] is not None and self.lastpick[1]+1 >= mb.daycount:
                ret += ' Your last pick was: '+str(self.lastpick[0])
            return ret
        else:
            return ''
