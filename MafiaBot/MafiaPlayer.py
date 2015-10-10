from MafiaItem import MafiaItem
from Items.itemlist import Items


class MafiaPlayer:

    FACTION_TOWN = 0
    FACTION_MAFIA = 1
    FACTION_MAFIATRAITOR = 2
    FACTION_THIRDPARTY = 3

    def __init__(self, name):
        self.name = name
        self.mafiachannel = None
        self.dead = True
        self.role = None
        self.faction = None
        self.items = dict()
        self.requiredaction = False
        self.mandatoryaction = False
        self.preventtownvictory = False
        self.itemused = dict()

    def IsDead(self):
        return self.dead

    def GetRolePM(self):
        ret = ''
        if self.faction == self.FACTION_TOWN:
            ret += 'You are aligned with the Town. You win if only people aligned with town are left alive. '
        elif self.faction == self.FACTION_MAFIA:
            ret += 'You are aligned with the Mafia. You win if the Mafia are the only players left alive or this cannot be prevented anymore. Join ' + self.mafiachannel + ' to meet your fellow mafia partners. '
        elif self.faction == self.FACTION_MAFIATRAITOR:
            ret += 'You are aligned with the Mafia. You win if the Mafia are the only players left alive or this cannot be prevented anymore. '
        elif self.faction == self.FACTION_THIRDPARTY:
            ret += 'You are a Third Party. Your win condition depends on your role. '
        if self.role is not None:
            ret += self.role.GetRolePM()
        return ret

    def UpdateActions(self):
        reqaction = False
        manaction = False
        if self.role is not None:
            if self.role.requiredaction:
                reqaction = True
            if self.role.mandatoryaction:
                manaction = True
        for item in self.items.values():
            # If an item with limited uses per type has already been used this night, we set the required actions of all of those types of items to False
            if item.type in self.itemused:
                if self.itemused[item.type]:
                    item.requiredaction = False
                    item.mandatoryaction = False
            if item.requiredaction:
                reqaction = True
            if item.mandatoryaction:
                manaction = True
        self.requiredaction = reqaction
        self.mandatoryaction = manaction

    def HandleCommand(self, command, param, bot, mb):
        if command == 'pass':
            if self.requiredaction:
                if self.role is not None:
                    if self.mandatoryaction:
                        return 'You cannot pass, you have mandatory actions to take.'
                    self.role.requiredaction = False
                for item in self.items.values():
                    item.requiredaction = False
                self.requiredaction = False
                return 'You decline taking further actions, for now.'
            return None

        elif command == 'use':
            if param is not None:
                paramsplits = param.split(' ', 1)
                if paramsplits[0].lower() in self.items:
                    # check if the type is limited in use and has already been used tonight:
                    if self.items[paramsplits[0].lower()].type in self.itemused:
                        if self.itemused[self.items[paramsplits[0].lower()].type]:
                            return 'You cannot use any more items of this type tonight.'
                    if len(paramsplits) > 1:
                        itemparam = paramsplits[1]
                    else:
                        itemparam = ''
                    returnpair = self.items[paramsplits[0].lower()].HandleCommand(itemparam, self, bot, mb)
                    if returnpair[0]:
                        # if it is a limited use item type, we mark it as used for the night
                        if self.items[paramsplits[0].lower()].type in self.itemused:
                            self.itemused[self.items[paramsplits[0].lower()].type] = True
                        del self.items[paramsplits[0].lower()]
                    return returnpair[1]

        elif command == 'items':
            retstr = 'You have the following items:'
            for item in self.items.values():
                if item.visible:
                    retstr += ' A ' + item.GetBaseName()+' called '+item.name+' received on night '+str(item.receiveday)+'.'
            return retstr

        else:
            if self.role is not None:
                # forward to role to handle
                return self.role.HandleCommand(command, param, bot, mb, self)

        return None

    def ReceiveItem(self, item, bot, mafiabot):
        i = 1
        if item in Items:
            basename = Items[item].GetBaseName()
            # find unique name
            while basename+str(i) in self.items:
                i += 1
            itemname = basename + str(i)
            self.items[itemname] = Items[item](itemname, mafiabot.daycount)
            itempm = self.items[itemname].ReceiveItemPM()
            if not itempm == '':
                bot.msg(self.name, itempm)

    def GetFaction(self):
        if self.faction == self.FACTION_MAFIA:
            return 'Mafia'
        elif self.faction == self.FACTION_TOWN:
            return 'Town'
        elif self.faction == self.FACTION_MAFIATRAITOR:
            return 'Mafia'
        elif self.faction == self.FACTION_THIRDPARTY:
            return 'Third Party'
        else:
            return 'None'

    def BeginNightPhase(self, mb, bot):
        nightactionstr = ''
        # reset limited uses for item types
        self.itemused = {MafiaItem.GUN: False, MafiaItem.SYRINGE: False, MafiaItem.CHECK: False}
        if self.role is not None:
            roleactionstr = self.role.BeginNightPhase(mb, self, bot)
            if not roleactionstr == '':
                nightactionstr += roleactionstr + ' '
        for item in self.items.values():
            itemactionstr = item.BeginNightPhase(mb, self, bot)
            if not itemactionstr == '':
                nightactionstr += itemactionstr + ' '
        self.UpdateActions()
        if not nightactionstr == '':
            bot.msg(self.name, 'You have to take the following night actions. Use !pass to skip on remaining night actions. '+nightactionstr.rstrip(), max_messages=10)

    def Kill(self, mb, bot, checkprotection):
        # only do something if we aren't already dead anyway
        if self.dead:
            return False, ''
        if checkprotection:
            # check all items for BP vest
            bpfound = False
            bpname = ''
            for pair in self.items.items():
                if pair[1].type == MafiaItem.VEST and not pair[1].fake:
                    bpname = pair[0]
                    bpfound = True
                    break
            if bpfound:
                # consume vest
                del self.items[bpname]
                # inform player of being hit
                bot.msg(self.name, "Ouch! You have been hit, but your bulletproof vest " + str(bpname) + " protected you.")
                # exit
                return False, ''
        self.dead = True
        # inform the player that they died
        bot.msg(self.name, "You have died. You may join the dead chat at "+mb.deadchat)
        if self.role is not None:
            self.role.Kill(bot, mb)
        flipmsg = ''
        if mb.revealfactionondeath:
            flipmsg += self.GetFaction()
        if self.role is not None and mb.revealrolesondeath:
            flipmsg += ' ' + self.role.GetRoleName()
        if not flipmsg == '':
            flipmsg = ', the ' + flipmsg
        return True, flipmsg

    def CheckSpecialWinCondition(self, mb):
        if self.role is not None:
            return self.role.CheckSpecialWinCondition(mb)
        else:
            return False

    def SpecialWin(self, winner, mb, bot):
        self.role.SpecialWin(winner, mb, bot)

    def NightKillPower(self):
        nkpower = 0
        # if the player has a real gun his night kill power increases by 1
        if [item for item in self.items.values() if item.type == MafiaItem.GUN and not item.fake]:
            nkpower += 1
        if self.role is not None:
            nkpower += self.role.NightKillPower()
        return nkpower

    def IsProbed(self):
        probed = False
        for item in self.items.values():
            if item.type == MafiaItem.PROBE:
                probed = True
        return probed
