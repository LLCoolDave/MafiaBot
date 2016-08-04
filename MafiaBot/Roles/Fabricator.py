from MafiaBot.MafiaRole import MafiaRole
from MafiaBot.MafiaAction import MafiaAction


class Fabricator(MafiaRole):

    def GetRolePM(self):
        ret = 'You are a Fabricator. You may give another player a fake item of your choice during the night. Possible items are: Background Check, Bulletproof Vest, Gun, Syringe, Bread'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName():
        return 'Fabricator'

    @staticmethod
    def GetRoleDescription():
        return 'Fabricators hand out fake items to other players at night. The possible items are: Background Check, Bulletproof Vest, Gun, Syringe, Bread'

    def HandleCommand(self, command, param, mb, player):
        if self.requiredaction:
            if command == 'send':
                if not self.limiteduses == 0:
                    splits = param.split(' ', 1)
                    if len(splits) == 2:
                        target = mb.GetPlayer(splits[0])
                        if target is not None:
                            if not target.IsDead():
                                if target is player:
                                    return 'You cannot give an item to yourself!'
                                else:
                                    itemstr = splits[1].lower()
                                    if itemstr == 'gun':
                                        item = 'fakegun'
                                    elif itemstr == 'vest':
                                        item = 'fakevest'
                                    elif itemstr == 'check':
                                        item = 'fakecheck'
                                    elif itemstr == 'syringe':
                                        item = 'fakesyringe'
                                    elif itemstr == 'bread':
                                        item = 'fakebread'
                                    else:
                                        return 'I do not know the item '+splits[1]
                                    mb.actionlist.append(MafiaAction(MafiaAction.SENDITEM, player, target, True, {'item': item}))
                                    self.requiredaction = False
                                    player.UpdateActions()
                                    ret = 'You send a ' + splits[1] + ' to '+str(target)+' tonight.'
                                    self.limiteduses -= 1
                                    if self.limiteduses > -1:
                                        ret += ' You have '+str(self.limiteduses)+' items remaining.'
                                    return ret
                        return 'Cannot find player '+splits[0]
                    return 'The command syntax is wrong. Use !send <target> <bread/check/gun/syringe/vest>.'

        return None

    def BeginNightPhase(self, mb, player):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Fabricator: You may send another player a fake item tonight. Use !send <player> <bread/check/gun/syringe/vest> to give that item to that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' items remaining.'
            return ret
        else:
            return ''
