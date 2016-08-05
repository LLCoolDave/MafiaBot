from .MafiaPlayer import MafiaPlayer
from collections import deque
from .Communication import CommunicationActions as CA
import discord
import traceback


class MessageQueueItem(object):

    def __init__(self, target, content):
        self.target = target
        self.content = content


class UpdateStatusQueueItem(object):

    def __init__(self, message):
        self.message = message


class SetRoleQueueItem(object):

    def __init__(self, target, role):
        self.target = target
        self.role = role


class SetChannelPermissionQueueItem(object):

    def __init__(self, channel, target, permissionoverwrite):
        self.channel = channel
        self.target = target
        self.permissionoverwrite = permissionoverwrite


class ResetAllQueueItem(object):
    pass


class DiscordCommunication(object):

    def __init__(self, client):
        self.client = client
        for server in client.servers:
            if server.name.lower() == 'mafia':
                self._server = server
                break
        self._commandqueue = deque()

        for channel in self._server.channels:
            if channel.name == 'gamechat':
                self.channel_game = channel
            elif channel.name == 'deadchat':
                self.channel_dead = channel
            elif channel.name == 'mafia':
                self.channel_mafia = channel

        for role in self._server.roles:
            if role.name == 'dead':
                self.role_dead = role
            elif role.name == 'playing':
                self.role_playing = role

        self.channels = [self.channel_game, self.channel_dead, self.channel_mafia]

        self.permission_allow_all = discord.PermissionOverwrite(read_messages=True, send_messages=True, send_TTS_messages=True, read_message_history=True)

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
                if not queueitem.content:
                    print(queueitem)
                    print(queueitem.target.name)
                await self.client.send_message(queueitem.target, queueitem.content)
            elif isinstance(queueitem, UpdateStatusQueueItem):
                await self.client.change_status(discord.Game(name=queueitem.message, type=0))
            elif isinstance(queueitem, SetRoleQueueItem):
                try:
                    if queueitem.role is None:
                        await self.client.replace_roles(queueitem.target)
                    else:
                        await self.client.replace_roles(queueitem.target, queueitem.role)
                except discord.Forbidden:
                    traceback.print_exc()
            elif isinstance(queueitem, SetChannelPermissionQueueItem):
                try:
                    await self.client.edit_channel_permissions(queueitem.channel, queueitem.target, queueitem.permissionoverwrite)
                except discord.Forbidden:
                    traceback.print_exc()
            elif isinstance(queueitem, ResetAllQueueItem):
                await self._reset_all()

    async def _reset_all(self):
        # first, revoke all roles
        for member in self._server.members:
            if not member == self.client.user:
                if len(member.roles) > 1:
                    try:
                        await self.client.replace_roles(member)
                    except discord.Forbidden:
                        traceback.print_exc()

        # next, revoke special permissions for mafia channel
        # ToDo: uses private attribute, unclean
        for overwrite in filter(lambda o: o.type == 'member', self.channel_mafia._permission_overwrites):
            member = discord.utils.get(self._server.members, id=overwrite.id)
            if member is not None:
                try:
                    await self.client.delete_channel_permissions(self.channel_mafia, member)
                except discord.Forbidden:
                    traceback.print_exc()

    def send(self, target, message, **kwargs):
        if isinstance(target, MafiaPlayer):
            target = str(target)
        if isinstance(target, str):
            target = self._find_user(target)
        self._commandqueue.append(MessageQueueItem(target, message))

    def action(self, target, action, *varargs, **kwargs):
        if isinstance(target, MafiaPlayer):
            target = str(target)
        if isinstance(target, str):
            target = self._find_user(target)

        if action == CA.SETSTATUS:
            self._commandqueue.append(UpdateStatusQueueItem(*varargs))
        elif action == CA.SETPLAYING:
            self._commandqueue.append(SetRoleQueueItem(target, self.role_playing))
        elif action == CA.SETDEAD:
            self._commandqueue.append(SetRoleQueueItem(target, self.role_dead))
        elif action == CA.RESET:
            self._commandqueue.append(SetRoleQueueItem(target, None))
            # ToDo: Should probably also revoke channel specific permissions
        elif action == CA.SETMAFIA:
            self._commandqueue.append(SetChannelPermissionQueueItem(self.channel_mafia, target, self.permission_allow_all))
        elif action == CA.RESETALL:
            self._commandqueue.append(ResetAllQueueItem())

    def get_id(self, name):
        try:
            return self._find_user(name).id
        except RuntimeError:
            return None

    def get_game_channel(self):
        return self.channel_game

    def get_dead_chat(self):
        return self.channel_dead

    def get_mafia_chat(self):
        return [self.channel_mafia]
