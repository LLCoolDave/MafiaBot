from MafiaBot.MafiaItem import MafiaItem
from sopel.tools import Identifier
from MafiaBot.MafiaAction import MafiaAction


class FakeBackgroundCheck(MafiaItem):

    def __init__(self, name, receiveday=0):
        super(FakeBackgroundCheck, self).__init__(name, receiveday)
        self.type = MafiaItem.CHECK
        self.fake = True

    def ReceiveItemPM(self):
        return 'You have received a background check! It is called '+self.name+'. You may use it during future nights to investigate another player\'s faction with the command !use '+self.name+' <target>.'

    @staticmethod
    def GetBaseName():
        return 'check'

    @staticmethod
    def ItemDescription():
        return 'Fake background checks pretend to provide a faction investigation to their owner. In reality, they always give a \'Town\' result.'

    def HandleCommand(self, param, player, bot, mb):
        if self.requiredaction:
            target = Identifier(param)
            if target in mb.players:
                if not mb.players[target].IsDead():
                    if mb.players[target] is player:
                        return 'You cannot investigate yourself!'
                    else:
                        mb.actionlist.append(MafiaAction(MafiaAction.CHECKFACTION, player.name, target, True, {'sanity': 'naive'}))
                        self.requiredaction = False
                        player.UpdateActions()
                        return True, 'You will investigate '+str(target)+' tonight.'
            return False, 'Cannot find player '+param
        return False, None

    def BeginNightPhase(self, mb, player, bot):
        self.requiredaction = True
        return 'Background Check: You may use your check '+self.name+' received on night '+str(self.receiveday)+' to investigate another player. To do so, use !use '+self.name+' <target>.'
