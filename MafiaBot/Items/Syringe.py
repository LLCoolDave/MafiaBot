from MafiaBot.MafiaItem import MafiaItem
from MafiaBot.MafiaAction import MafiaAction


class Syringe(MafiaItem):

    def __init__(self, name, receiveday=0):
        super(Syringe, self).__init__(name, receiveday)
        self.type = MafiaItem.SYRINGE

    def ReceiveItemPM(self):
        return 'You have received a syringe! It is called '+self.name+'. You may use it during future nights to protect a player from a night kill with the command !use '+self.name+' <target>.'

    @staticmethod
    def GetBaseName():
        return 'syringe'

    @staticmethod
    def ItemDescription():
        return 'Syringes provide protection to a player during the night. Using them protects the target from one night kill that night.'

    def HandleCommand(self, param, player, mb):
        if self.requiredaction:
            target = mb.GetPlayer(param)
            if target is not None:
                if not target.IsDead():
                    mb.actionlist.append(MafiaAction(MafiaAction.PROTECT, player, target, True))
                    self.requiredaction = False
                    player.UpdateActions()
                    return True, 'You will protect '+str(target)+' tonight.'
            return False, 'Cannot find player '+param
        return False, None

    def BeginNightPhase(self, mb, player):
        self.requiredaction = True
        return 'Syringe: You may use your syringe '+self.name+' received on night '+str(self.receiveday)+' to protect a player. To do so, use !use '+self.name+' <target>.'
