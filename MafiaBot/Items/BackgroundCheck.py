from MafiaBot.MafiaItem import MafiaItem
from MafiaBot.MafiaAction import MafiaAction


class BackgroundCheck(MafiaItem):

    def __init__(self, name, receiveday=0):
        super(BackgroundCheck, self).__init__(name, receiveday)
        self.type = MafiaItem.CHECK

    def ReceiveItemPM(self):
        return 'You have received a background check! It is called '+self.name+'. You may use it during future nights to investigate another player\'s faction with the command !use '+self.name+' <target>.'

    @staticmethod
    def GetBaseName():
        return 'check'

    @staticmethod
    def ItemDescription():
        return 'Background checks provide a faction investigation to their owner.'

    def HandleCommand(self, param, player, mb):
        if self.requiredaction:
            target = mb.GetPlayer(param)
            if target is not None:
                if not target.IsDead():
                    if target is player:
                        return 'You cannot investigate yourself!'
                    else:
                        mb.actionlist.append(MafiaAction(MafiaAction.CHECKFACTION, player, target, True, {'sanity': 'sane'}))
                        self.requiredaction = False
                        player.UpdateActions()
                        return True, 'You will investigate '+str(target)+' tonight.'
            return False, 'Cannot find player '+param
        return False, None

    def BeginNightPhase(self, mb, player):
        self.requiredaction = True
        return 'Background Check: You may use your check '+self.name+' received on night '+str(self.receiveday)+' to investigate another player. To do so, use !use '+self.name+' <target>.'
