from .models import Y2021Settings
from .teamwork import AsyncTeamworkTimeConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.urls import reverse

class TeamNotificationsConsumer(AsyncTeamworkTimeConsumer):
    def setup(self):
        super(TeamNotificationsConsumer, self).setup(None)

    async def connect(self):
        if await database_sync_to_async(get_enabled)():
            await super(TeamNotificationsConsumer, self).connect()

    async def handle(self, msg):
        pass

    async def join_or_create_session(self):
        self.group = await database_sync_to_async(get_group)(self.team)
        await self.channel_layer.group_add(self.group, self.channel_name)

def get_enabled():
    try:
        Y2021Settings.objects.get(name='disable_notifications')
    except Y2021Settings.DoesNotExist:
        return True

def is_it_hunt():
    try:
        setting = Y2021Settings.objects.get_or_create(name='is_it_hunt_yet')[0]
        return setting.value == 'TRUE'
    except Y2021Settings.DoesNotExist:
        return False

def get_group(team):
    return 'notifications-%s' % team.y2021teamdata.tempest_id

def notify_team_log(team, event_type, message, object_id, link, time):
    iih = is_it_hunt()
    if get_enabled() and (iih or team.is_special or team.is_admin):
        async_to_sync(get_channel_layer().group_send)(
            get_group(team), {'type': 'channel.receive_broadcast', 'data': {
                'event_type': event_type, 'message': message, 'link': link}})

def notify_hq_update(update, teams):
    iih = is_it_hunt()
    if get_enabled():
        for team in teams:
            if iih or team.is_special or team.is_admin:
                async_to_sync(get_channel_layer().group_send)(
                    get_group(team), {'type': 'channel.receive_broadcast', 'data': {
                        'event_type': 'hq_update',
                        'message': 'HQ Update: %s' % update.subject,
                        'link': reverse('updates')}})

def notify_mmo_unlocked(team):
    if get_enabled():
        async_to_sync(get_channel_layer().group_send)(
            get_group(team), {'type': 'channel.receive_broadcast', 'data': {
                'event_type': 'important', 'special': 'important', 'message': 'Important Message from Yew Labs', 'link': '/device_message/'}})

def notify_hunt_launched(team):
    if get_enabled():
        async_to_sync(get_channel_layer().group_send)(
            get_group(team), {'type': 'channel.receive_broadcast', 'data': {
                'event_type': 'important', 'special': 'important', 'message': 'Yew Labs Data Available', 'link': '/'}})
