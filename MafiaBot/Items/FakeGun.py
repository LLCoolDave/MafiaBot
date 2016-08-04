from MafiaBot.MafiaItem import MafiaItem
from MafiaBot.MafiaAction import MafiaAction


class FakeGun(MafiaItem):

    def __init__(self, name, receiveday=0):
        super(FakeGun, self).__init__(name, receiveday)
        self.type = MafiaItem.GUN
        self.fake = True

    def ReceiveItemPM(self):
        return 'You have received a gun! It is called '+self.name+'. You may use it during future nights to kill another player with the command !use '+self.name+' <target>.'

    @staticmethod
    def GetBaseName():
        return 'gun'

    @staticmethod
    def ItemDescription():
        return 'Fake guns disguise themselves as real guns. If they are fired during the night, they backfire and kill their owner instead.'

    def HandleCommand(self, param, player, mb):
        if self.requiredaction:
            target = mb.GetPlayer(param)
            if target is not None:
                if not target.IsDead():
                    if target is player:
                        return 'You cannot shoot yourself!'
                    else:
                        mb.actionlist.append(MafiaAction(MafiaAction.KILL, player, player, False))
                        self.requiredaction = False
                        player.UpdateActions()
                        return True, 'You will shoot '+str(target)+' tonight.'
            return False, 'Cannot find player '+param
        return False, None

    def BeginNightPhase(self, mb, player):
        self.requiredaction = True
        return 'Gun: You may fire your gun '+self.name+' received on night '+str(self.receiveday)+' to kill another player. To do so, use !use '+self.name+' <target>.'
