__author__ = 'LLCoolDave'

from MafiaItem import MafiaItem

class MafiaPlayer:

    FACTION_TOWN = 0
    FACTION_MAFIA = 1

    def __init__(self, name):
        self.name = name
        self.mafiachannel = None
        self.dead = True
        self.role = None
        self.faction = None
        self.items = dict()
        self.requiredAction = False

    def IsDead(self):
        return self.dead

    def GetRolePM(self):
        ret = ''
        if self.faction == self.FACTION_TOWN:
            ret += 'You are aligned with the Town. You win if only people aligned with town are left alive.\n'
        elif self.faction == self.FACTION_MAFIA:
            ret += 'You are aligned with the Mafia. You win if the Mafia are the only players left alive or this cannot be prevented anymore. Join '+ self.mafiachannel + ' to meet your fellow mafia partners.\n'
        if self.role is not None:
            ret += self.role.GetRolePM()
        return ret

    def HandleCommand(self, command, param, bot, mb):
        if command == 'pass':
            if self.requiredAction:
                if self.role is not None:
                    if self.role.mandatoryaction:
                        return 'You cannot pass, you have mandatory actions to take.'
                self.requiredAction = False
                return 'You decline taking further actions, for now.'
            return None

        elif command == 'use':
            paramsplits = param.split(' ', 1)
            if paramsplits[0] in self.items:
                if len(paramsplits) > 1:
                    itemparam = paramsplits[1]
                else:
                    itemparam = ''
                return self.items[paramsplits[0]].HandleCommand(itemparam, bot, mb)

        else:
            if self.role is not None:
                # forward to role to handle
                return self.role.HandleCommand(command, param, bot, mb, self)

        return None

    def Kill(self, mb, checkprotection):
        if checkprotection:
            # check all items for BP vest
            bpfound = False
            bpname = ''
            for pair in self.items.items():
                if pair[1].type == MafiaItem.VEST:
                    bpname = pair[0]
                    bpfound = True
                    break
            if bpfound:
                # consume vest
                del self.items[bpname]
                # inform player of being hit
                mb.msg(self.name, "Ouch! You have been hit, but your bulletproof vest protected you.")
                # exit
                return False, ''
        self.dead = True
        flipmsg = ''
        if mb.revealfactionondeath:
            if self.faction == self.FACTION_MAFIA:
                flipmsg += 'Mafia'
            elif self.faction == self.FACTION_TOWN:
                flipmsg += 'Town'
        if self.role is not None and mb.revealroleondeath:
            flipmsg += ' ' + self.role.GetRoleName()
        if not flipmsg == '':
            flipmsg = ', the ' + flipmsg
        return True, flipmsg
