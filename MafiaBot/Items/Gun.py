from MafiaBot.MafiaItem import MafiaItem
from MafiaBot.MafiaAction import MafiaAction


class Gun(MafiaItem):

    def __init__(self, name, receiveday=0):
        super(Gun, self).__init__(name, receiveday)
        self.type = MafiaItem.GUN

    def ReceiveItemPM(self):
        return 'You have received a gun! It is called '+self.name+'. You may use it during future nights to kill another player with the command !use '+self.name+' <target>.'

    @staticmethod
    def GetBaseName():
        return 'gun'

    @staticmethod
    def ItemDescription():
        return 'Guns provide a night kill to their owner. They can be fire alongside other night actions, but at most one gun may be used by each player each night.'

    def HandleCommand(self, param, player, mb):
        if self.requiredaction:
            target = mb.GetPlayer(param)
            if target is not None:
                if not target.IsDead():
                    if target is player:
                        return 'You cannot shoot yourself!'
                    else:
                        mb.actionlist.append(MafiaAction(MafiaAction.KILL, player, target, True))
                        self.requiredaction = False
                        player.UpdateActions()
                        return True, 'You will shoot '+str(target)+' tonight.'
            return False, 'Cannot find player '+param
        return False, None

    def BeginNightPhase(self, mb, player):
        self.requiredaction = True
        return 'Gun: You may fire your gun '+self.name+' received on night '+str(self.receiveday)+' to kill another player. To do so, use !use '+self.name+' <target>.'
