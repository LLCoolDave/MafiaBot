__author__ = 'LLCoolDave'

class MafiaAction:

    KILL = 0
    BLOCK = 1
    PROTECT = 2
    CHECKROLE = 3
    CHECKFACTION = 4

    def __init__(self, actiontype, source, target, visiting):
        self.actiontype = actiontype
        self.source = source
        self.target = target
        self.visiting = visiting