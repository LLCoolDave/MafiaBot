from MafiaBot.MafiaRole import MafiaRole
from MafiaBot.MafiaPlayer import MafiaPlayer


class Traitor(MafiaRole):

    def GetRolePM(self):
        return 'You are a Traitor. You are secretly aligned with the Mafia, but even they don\'t know of your existence.'

    @staticmethod
    def GetRoleName():
        return 'Traitor'

    @staticmethod
    def GetRoleDescription():
        return 'Traitors are the secret Mafia. They have no night kill power, they do not participate in the Mafia night discussion. In fact, the Mafia don\'t even know they exist or who they are. However, the Traitors do know the Mafia and attempt to steer the day actions in their favor. Traitors win with the Mafia, as long as any of them are still alive.'

    def StartGame(self, player, mafiabot):
        # we get a list of the mafia to send to the player
        mafia = [str(pl) for pl in mafiabot.players.values() if pl.faction == MafiaPlayer.FACTION_MAFIA]
        mafiabot.Send(player.name, 'The Mafia this game are: '+', '.join(mafia))
