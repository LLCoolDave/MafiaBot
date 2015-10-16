class MafiaAction:

    KILL = 0
    BLOCK = 1
    PROTECT = 2
    CHECKROLE = 3
    CHECKFACTION = 4
    TRACK = 5
    WATCH = 6
    VISIT = 7
    SENDITEM = 8

    # for generic callbacks
    CALLBACK = 255

    # String lookup table
    Lookup = {KILL: 'Kill',
              BLOCK: 'Roleblock',
              PROTECT: 'Protect',
              CHECKROLE: 'Rolecheck',
              CHECKFACTION: 'Factioncheck',
              TRACK: 'Track',
              WATCH: 'Watch',
              VISIT: 'Visit',
              SENDITEM: 'Send item',
              CALLBACK: 'Special'}

    def __init__(self, actiontype, source, target, visiting, modifiers=None):
        self.actiontype = actiontype
        self.source = source
        self.target = target
        self.visiting = visiting
        if modifiers is None:
            self.modifiers = dict()
        else:
            self.modifiers = modifiers
