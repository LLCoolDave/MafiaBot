from MafiaBot.MafiaRole import MafiaRole
from MafiaBot.MafiaAction import MafiaAction


class Jailer(MafiaRole):

    def __init__(self, settings=dict()):
        super(Jailer, self).__init__(settings)
        self.lastpick = (None, 0)

    def GetRolePM(self):
        ret = 'You are a Jailer. You may roleblock and protect another player at the same time during the night. You cannot pick the same player on two consecutive nights.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName():
        return 'Jailer'

    @staticmethod
    def GetRoleDescription():
        return 'Jailers are combined prostitutes and medics. They disable the active abilities of another player at night while also protecting them from one night kill. Roleblocks do not interfer with each other, but prevent all other actions by the blocked player. A jailer may not pick the same player on two consecutive nights.'

    def HandleCommand(self, command, param, mb, player):
        if self.requiredaction:
            if command == 'block' or command == 'protect':
                if not self.limiteduses == 0:
                    target = mb.GetPlayer(param)
                    if self.lastpick[0] is None or self.lastpick[1]+1 < mb.daycount:
                        lastpick = None
                    else:
                        lastpick = self.lastpick[0]
                    if target is not None:
                        if not target.IsDead():
                            if target is player or target is lastpick:
                                return 'You cannot jail that player.'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.BLOCK, player, target, True, {'faction': player.faction}))
                                mb.actionlist.append(MafiaAction(MafiaAction.PROTECT, player, target, True))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You jail '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                self.lastpick = (target, mb.daycount)
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' jails remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Jailer: You may roleblock and protect another player tonight. Use !block <player> or !protect <player> to jail that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' uses remaining.'
            if self.lastpick[0] is not None and self.lastpick[1]+1 >= mb.daycount:
                ret += ' Your last pick was: '+str(self.lastpick[0])
            return ret
        else:
            return ''
