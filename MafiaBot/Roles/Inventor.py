from MafiaBot.MafiaRole import MafiaRole
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction


class Inventor(MafiaRole):

    def __init__(self, settings=dict()):
        super(Inventor, self).__init__(settings)
        self.items = {'gun': 1, 'vest': 1, 'check': 1, 'syringe': 1}

    def GetRolePM(self):
        ret = 'You are an Inventor. You may give another player a item of your choice during the night. You only have one copy of each item. Possible items are: Background Check, Bulletproof Vest, Gun, Syringe'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName():
        return 'Inventor'

    @staticmethod
    def GetRoleDescription():
        return 'Inventors hand out items to other players at night. They only have one copy of each item. The possible items are: Background Check, Bulletproof Vest, Gun, Syringe'

    def HandleCommand(self, command, param, bot, mb, player):
        if self.requiredaction:
            if command == 'send':
                if not self.limiteduses == 0:
                    splits = param.split(' ', 1)
                    if len(splits) == 2:
                        target = Identifier(splits[0])
                        if target in mb.players:
                            if not mb.players[target].IsDead():
                                if mb.players[target] is player:
                                    return 'You cannot give an item to yourself!'
                                else:
                                    itemstr = splits[1].lower()
                                    if not (itemstr == 'gun' or itemstr == 'vest' or itemstr == 'check' or itemstr == 'syringe'):
                                        return 'I do not know the item '+splits[1]
                                    if self.items[itemstr] == 0:
                                        return 'You have already handed out your copy of '+splits[1]
                                    mb.actionlist.append(MafiaAction(MafiaAction.SENDITEM, player.name, target, True, {'item': itemstr}))
                                    self.items[itemstr] = 0
                                    self.requiredaction = False
                                    player.UpdateActions()
                                    ret = 'You send a ' + splits[1] + ' to '+str(target)+' tonight.'
                                    self.limiteduses -= 1
                                    if self.limiteduses > -1:
                                        ret += ' You have '+str(self.limiteduses)+' uses remaining.'
                                    return ret
                        return 'Cannot find player '+splits[0]
                    return 'The command syntax is wrong. Use !send <target> <check/gun/syringe/vest>.'

        return None

    def BeginNightPhase(self, mb, player, bot):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Inventor: You may send another player an item tonight. Use !send <player> <check/gun/syringe/vest> to give that item to that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' uses remaining.'
            ret += ' Your remaining items are: '
            items = []
            if self.items['check'] == 1:
                items.append('Background Check')
            if self.items['vest'] == 1:
                items.append('Bulletproof Vest')
            if self.items['gun'] == 1:
                items.append('Gun')
            if self.items['syringe'] == 1:
                items.append('Syringe')
            ret += ', '.join(items)
            return ret.rstrip()
        else:
            return ''
