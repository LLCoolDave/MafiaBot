from .MafiaPlayer import MafiaPlayer
from collections import deque


class MessageQueueItem(object):

    def __init__(self, target, content):
        # debug
        if isinstance(target, str):
            print(content)
        self.target = target
        self.content = content


class DiscordCommunication(object):

    def __init__(self, client):
        self.client = client
        for server in client.servers:
            if server.name.lower() == 'mafia':
                self._server = server
                break
        self._commandqueue = deque()

    def _find_user(self, name):
        if isinstance(name, MafiaPlayer):
            name = str(name)

        # look up by name
        user = None
        for member in self._server.members:
            if member.name.lower() == name.lower():
                user = member
        if user is not None:
            return user
        # might have received an id
        user = self._server.get_member(name)
        if user is not None:
            return user
        else:
            raise RuntimeError('Could not find user %s' % user)

    async def process_queue(self):
        while self._commandqueue:
            queueitem = self._commandqueue.popleft()
            if isinstance(queueitem, MessageQueueItem):
                await self.client.send_message(queueitem.target, queueitem.content)

    def send(self, target, message, **kwargs):
        if isinstance(target, MafiaPlayer):
            target = str(target)
        if isinstance(target, str):
            target = self._find_user(target)
        self._commandqueue.append(MessageQueueItem(target, message))

    def action(self, *varargs):
        pass

    def join(self, channel):
        pass

    def leave(self, channel):
        pass

    def get_id(self, name):
        try:
            return self._find_user(name).id
        except RuntimeError:
            return None

    def get_game_channel(self):
        for channel in self.client.get_all_channels():
            if channel.name == 'gamechat':
                return channel

    def get_dead_chat(self):
        for channel in self.client.get_all_channels():
            if channel.name == 'deadchat':
                return channel

    def get_mafia_chat(self):
        for channel in self.client.get_all_channels():
            if channel.name == 'mafia':
                return [channel]
