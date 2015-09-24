__author__ = 'LLCoolDave'

class MafiaPlayer:

    FACTION_TOWN = 0
    FACTION_MAFIA = 1

    def __init__(self):
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
                return self.role.HandleCommand(command, param, bot, mb)

        return None

    def Kill(self, mb):
        self.dead = True
        if self.role is not None:
            return self.role.GetRoleName()
        else:
            return ''
