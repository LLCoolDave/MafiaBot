from MafiaBot.MafiaRole import MafiaRole


class Goon(MafiaRole):

    def GetRolePM(self):
        return 'You are a Goon. You have no special abilities outside of participating in the night chat.'

    def GetRoleName(self):
        return 'Goon'

    @staticmethod
    def GetRoleDescription():
        return 'Goons are the basic henchmen of the Mafia. They have no special abilities, but participate in the night chat and can carry out the faction kills.'
