from MafiaBot.MafiaItem import MafiaItem


class FakeVest(MafiaItem):

    def __init__(self, name, receiveday=0):
        super(FakeVest, self).__init__(name, receiveday)
        self.fake = True
        self.type = MafiaItem.VEST

    def ReceiveItemPM(self):
        return 'You have received a bulletproof vest! It is called '+self.name+'. It will protect you from one night kill. You will be informed when it has been used.'

    @staticmethod
    def GetBaseName():
        return 'vest'

    @staticmethod
    def ItemDescription():
        return 'Fake bulletproof vests pretend to protect their owners. In reality, they do nothing at all.'

    def HandleCommand(self, param, player, mb):
        return False, None

    def BeginNightPhase(self, mb, player):
        return ''
