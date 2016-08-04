from MafiaBot.MafiaRole import MafiaRole
from MafiaBot.MafiaAction import MafiaAction
from MafiaBot.Items.Probe import Probe


class Alien(MafiaRole):

    def GetRolePM(self):
        return 'You are an Alien. You may secretly probe other players during the night. Once you have probed all other remaining living players, you win the game. You may use !probes to see a list of probed players.'

    @staticmethod
    def GetRoleName():
        return 'Alien'

    @staticmethod
    def GetRoleDescription():
        return 'Aliens probe other players at night. Once they have probed all other living players, they win the game.'

    def HandleCommand(self, command, param, mb, player):
        if command == 'probes':
            # get all other probed players
            probed = [str(pl.name) for pl in mb.players.values() if (pl.IsProbed() and not pl.IsDead() and pl is not player)]
            return 'The probed players are: '+', '.join(probed)
        elif self.requiredaction:
            if command == 'visit':
                if not self.limiteduses == 0:
                    target = mb.GetPlayer(param)
                    if target is not None:
                        if not target.IsDead():
                            if target is player:
                                return 'You cannot give a probe to yourself!'
                            else:
                                mb.actionlist.append(MafiaAction(MafiaAction.SENDITEM, player, target, True, {'item': 'probe'}))
                                self.requiredaction = False
                                player.UpdateActions()
                                ret = 'You probe '+str(target)+' tonight.'
                                return ret
                    return 'Cannot find player '+param
        return None

    def BeginNightPhase(self, mb, player):
        self.requiredaction = True
        return 'Alien: You may probe another player tonight. Use !visit <player> to probe that player.'

    def CheckSpecialWinCondition(self, mb):
        # get a list of all alive players that are not probed
        unprobed = [str(player.name) for player in mb.players.values() if (not player.IsProbed() and not player.IsDead())]
        if unprobed:
            return False
        else:
            return True

    def SpecialWin(self, winner, mb):
        mb.Send(mb.mainchannel, 'The Alien wins this game! Congratulations to '+str(winner.name), max_messages=10)
        mb.Send(mb.mainchannel, 'The roles this game were - '+mb.GetRoleList(), max_messages=10)

    def StartGame(self, player, mafiabot):
        # hand probe to self. Makes checking for victory a lot easier
        player.items['probe1'] = Probe('probe1', 0)

