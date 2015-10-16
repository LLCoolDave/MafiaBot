from MafiaBot.MafiaRole import MafiaRole
from MafiaBot.Items.BulletproofVest import BulletproofVest


class Bulletproof(MafiaRole):

    def GetRolePM(self):
        return 'You are a Bulletproof. You start the game with one bulletproof vest.'

    @staticmethod
    def GetRoleName(self):
        return 'Bulletproof'

    @staticmethod
    def GetRoleDescription():
        return 'Bulletproofs have no special abilities, but start the game with one bulletproof vest. It protects them from one night kill and is then consumed.'

    def StartGame(self, bot, player, mafiabot):
        player.items['vest1'] = BulletproofVest('vest1', 0)
