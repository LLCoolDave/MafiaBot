__author__ = 'LLCoolDave'


class ResistancePlayer:

    FACTION_RESISTANCE = 0
    FACTION_SPIES = 1

    def __init__(self, nick):
        self.nick = nick
        self.faction = None
