from MafiaBot.MafiaItem import MafiaItem
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction


class BulletproofVest(MafiaItem):

    def __init__(self, name, receiveday=0):
        super(BulletproofVest, self).__init__(name, receiveday)
        self.type = MafiaItem.VEST

    def ReceiveItemPM(self):
        return 'You have received a bulletproof vest! It is called '+self.name+'. It will protect you from one night kill. You will be informed when it has been used.'

    @staticmethod
    def GetBaseName():
        return 'vest'

    def ItemDescription(self):
        return 'Bulletproof vests protect their owners. They counteract one night kill and are then consumed. Their owner is informed when this happens.'

    def HandleCommand(self, param, player, bot, mb):
        return False, None

    def BeginNightPhase(self, mb, player, bot):
        return 'Vest: You have a bulletproof vest called '+self.name+' received on night '+str(self.receiveday)+'.'
