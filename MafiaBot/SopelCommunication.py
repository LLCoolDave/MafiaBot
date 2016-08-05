from sopel.tools import Identifier
from .MafiaPlayer import MafiaPlayer
import random
from .Communication import CommunicationActions as CA


class SopelCommunication(object):

    def __init__(self, bot):
        self.bot = bot

    def send(self, target, message, **kwargs):
        if isinstance(target, MafiaPlayer):
            target = target.name
        self.bot.msg(Identifier(target), message, **kwargs)

    def action(self, target, action, *varargs, **kwargs):
        if action == CA.HIDDEN:
            self.bot.write('MODE ', str(target) + ' +s')
        elif action == CA.JOIN:
            self.bot.join(target)
        elif action == CA.LEAVE:
            self.bot.part(target)

    def get_id(self, name):
        return str(name).lower()

    def get_game_channel(self):
        return Identifier('#fridaynightmafia')

    def get_dead_chat(self):
        return '#deadchat'+str(random.randrange(10000))

    def get_mafia_chat(self):
        return ['#mafia'+str(random.randrange(10000))]
