from MafiaBot.MafiaRole import MafiaRole


class Oracle(MafiaRole):

    def __init__(self, settings=dict()):
        super(Oracle, self).__init__(settings)
        self.target = None

    def GetRolePM(self):
        ret = 'You are an Oracle. You may pick another player at night. If you die, the faction and role of the last picked player will be revealed.'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName():
        return 'Oracle'

    @staticmethod
    def GetRoleDescription():
        return 'Oracles pick other players at night. If they die, the faction and role of their last picked target will be revealed.'

    def HandleCommand(self, command, param, mb, player):
        if self.requiredaction:
            if command == 'pick':
                if not self.limiteduses == 0:
                    target = mb.GetPlayer(param)
                    if target is not None:
                        if not target.IsDead():
                            if target is player:
                                return 'You cannot pick yourself!'
                            else:
                                self.target = target
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You pick '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' picks remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Oracle: You may pick another player tonight. Use !pick <player> to pick that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' picks remaining.'
            return ret
        else:
            return ''

    def Kill(self, mafiabot):
        if self.target is not None:
            if self.target.role is not None:
                rolestr = ' '+self.target.role.GetRoleName()
            else:
                rolestr = ''
            mafiabot.Send.msg(mafiabot.mainchannel, 'The oracle reveals that '+str(self.target)+' is a '+self.target.GetFaction()+rolestr+'.')
