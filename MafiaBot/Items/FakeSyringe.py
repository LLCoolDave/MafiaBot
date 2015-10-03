from MafiaBot.MafiaItem import MafiaItem
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction


class FakeSyringe(MafiaItem):

    def __init__(self, name, receiveday=0):
        super(FakeSyringe, self).__init__(name, receiveday)
        self.type = MafiaItem.SYRINGE
        self.fake = True

    def ReceiveItemPM(self):
        return 'You have received a syringe! It is called '+self.name+'. You may use it during future nights to protect a player from a night kill with the command !use '+self.name+' <target>.'

    @staticmethod
    def GetBaseName():
        return 'syringe'

    @staticmethod
    def ItemDescription():
        return 'Fake Syringes pretend to provide protection to a player during the night. In reality, they are a mere placebo and accomplish nothing.'

    def HandleCommand(self, param, player, bot, mb):
        if self.requiredaction:
            target = Identifier(param)
            if target in mb.players:
                if not mb.players[target].IsDead():
                    self.requiredaction = False
                    player.UpdateActions()
                    return True, 'You will protect '+str(target)+' tonight.'
            return False, 'Cannot find player '+param
        return False, None

    def BeginNightPhase(self, mb, player, bot):
        self.requiredaction = True
        return 'Syringe: You may use your syringe '+self.name+' received on night '+str(self.receiveday)+' to protect a player. To do so, use !use '+self.name+' <target>.'
