__author__ = 'LLCoolDave'

class MafiaItem:

    GUN = 0
    SYRINGE = 1
    VEST = 2

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def ReceiveItemPM(self):
        return ''

    def ItemDescription(self):
        return ''

    def HandleCommand(self, param, bot, mb):
        return None