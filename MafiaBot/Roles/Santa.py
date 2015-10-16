from MafiaBot.MafiaRole import MafiaRole
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction
import random


class Santa(MafiaRole):

    def GetRolePM(self):
        ret = 'You are a Santa. You may give another player a random item during the night. Possible items are: Background Check, Bulletproof Vest, Gun, Syringe'
        if self.limiteduses > -1:
            ret += ' You may only use this ability '+str(self.limiteduses)+' times.'
        return ret

    @staticmethod
    def GetRoleName():
        return 'Santa'

    @staticmethod
    def GetRoleDescription():
        return 'Santas hand out random items to other players at night. The possible items are: Background Check, Bulletproof Vest, Gun, Syringe'

    def HandleCommand(self, command, param, bot, mb, player):
        if self.requiredaction:
            if command == 'send':
                if not self.limiteduses == 0:
                    target = Identifier(param)
                    if target in mb.players:
                        if not mb.players[target].IsDead():
                            if mb.players[target] is player:
                                return 'You cannot give a present to yourself!'
                            else:
                                rnd = random.randint(1, 4)
                                if rnd == 1:
                                    item = 'gun'
                                elif rnd == 2:
                                    item = 'vest'
                                elif rnd == 3:
                                    item = 'check'
                                elif rnd == 4:
                                    item = 'syringe'
                                else:
                                    item = ''
                                mb.actionlist.append(MafiaAction(MafiaAction.SENDITEM, player.name, target, True, {'item': item}))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You send a present to '+str(target)+' tonight.'
                                self.limiteduses -= 1
                                if self.limiteduses > -1:
                                    ret += ' You have '+str(self.limiteduses)+' presents remaining.'
                                return ret
                    return 'Cannot find player '+param

        return None

    def BeginNightPhase(self, mb, player, bot):
        if not self.limiteduses == 0:
            self.requiredaction = True
            ret = 'Santa: You may send another player a present tonight. Use !send <player> to give a random item to that player.'
            if self.limiteduses > -1:
                ret += ' You have '+str(self.limiteduses)+' presents remaining.'
            return ret
        else:
            return ''
