class MafiaItem(object):

    GUN = 0
    SYRINGE = 1
    VEST = 2
    CHECK = 3
    BREAD = 4
    PROBE = 5

    def __init__(self, name, receiveday=0):
        self.name = name
        self.type = None
        self.requiredaction = False
        self.mandatoryaction = False
        self.receiveday = receiveday
        self.fake = False
        self.visible = True

    def ReceiveItemPM(self):
        return ''

    @staticmethod
    def GetBaseName():
        return ''

    @staticmethod
    def ItemDescription():
        return ''

    def HandleCommand(self, param, player, mb):
        return False, None

    def BeginNightPhase(self, mb, player):
        return ''
