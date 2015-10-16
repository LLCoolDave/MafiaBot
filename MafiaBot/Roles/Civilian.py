from MafiaBot.MafiaRole import MafiaRole


class Civilian(MafiaRole):

    def GetRolePM(self):
        return 'You are a Civilian. You have no special abilities.'

    @staticmethod
    def GetRoleName(self):
        return 'Civilian'

    @staticmethod
    def GetRoleDescription():
        return 'Civilians constitute the uninformed majority of the Town. They do not have any special knowledge or actions, but must try to identify the Mafia and get them lynched during the day phases of the game.'