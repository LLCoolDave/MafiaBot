from MafiaBot.MafiaItem import MafiaItem
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction


class Probe(MafiaItem):

    def __init__(self, name, receiveday=0):
        super(Probe, self).__init__(name, receiveday)
        self.type = MafiaItem.PROBE
        self.visible = False

    def ReceiveItemPM(self):
        return ''

    @staticmethod
    def GetBaseName():
        return 'probe'

    @staticmethod
    def ItemDescription():
        return 'Probes are handed out by Aliens. Players do not know if and when they are probed. Once all non-Aliens alive in the game are probed, the Alien wins the game.'

    def HandleCommand(self, param, player, bot, mb):
        return False, None

    def BeginNightPhase(self, mb, player, bot):
        return ''
