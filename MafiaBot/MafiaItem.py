class MafiaItem(object):

    GUN = 0
    SYRINGE = 1
    VEST = 2

    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.requiredaction = False
        self.mandatoryaction = False

    def ReceiveItemPM(self):
        return ''

    def ItemDescription(self):
        return ''

    def HandleCommand(self, param, bot, mb):
        return None

    def BeginNightPhase(self, mb, player, bot):
        return ''
