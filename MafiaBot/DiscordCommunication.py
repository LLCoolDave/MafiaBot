from .MafiaPlayer import MafiaPlayer


class SopelCommunication(object):

    def __init__(self, bot):
        self.bot = bot

    def send(self, target, message, **kwargs):
        if isinstance(target, MafiaPlayer):
            target = target.name
        self.bot.msg(Identifier(target), message, **kwargs)

    def action(self, *varargs):
        pass

    def join(self, channel):
        pass

    def leave(self, channel):
        pass

    def get_id(self, name):
        return str(name).lower()

    def get_game_channel(self):
        return Identifier('#fridaynightmafia')

    def get_dead_chat(self):
        return '#deadchat'+str(random.randrange(10000))

    def get_mafia_chat(self):
        return ['#mafia'+str(random.randrange(10000))]


class DiscordChannelWrapper(object):

