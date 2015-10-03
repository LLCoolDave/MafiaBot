from MafiaBot.MafiaItem import MafiaItem
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction


class FakeBread(MafiaItem):

    def __init__(self, name, receiveday=0):
        super(FakeBread, self).__init__(name, receiveday)
        self.fake = True
        self.type = MafiaItem.BREAD
        self.visible = False

    def ReceiveItemPM(self):
        return 'You have received a loaf of bread! It is called '+self.name+'. Considering you haven\'t seen a baker around in town, you should rather not eat it.'

    @staticmethod
    def GetBaseName():
        return 'bread'

    @staticmethod
    def ItemDescription():
        return 'Fake bread does nothing. It doesn\'t even confuse players as there is no real bread it could be mistaken for. A curious item indeed.'

    def HandleCommand(self, param, player, bot, mb):
        return False, None

    def BeginNightPhase(self, mb, player, bot):
        return ''
