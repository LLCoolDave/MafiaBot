class SopelCommunication(object):

    def __init__(self, bot):
        self.bot = bot

    def send(self, target, message, **kwargs):
        self.bot.msg(target, message, **kwargs)

    def action(self, *varargs):
        self.bot.write(tuple(*varargs))

    def join(self, channel):
        self.bot.join(channel)

    def leave(self, channel):
        self.bot.part(channel)
