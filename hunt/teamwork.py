from django.db import models
from django.db import transaction

from hunt.models import TeamworkSession, Y2021PuzzleData
import spoilr.log as log
from spoilr.models import Team, Puzzle, PuzzleAccess

import json
import logging
import time
import uuid

from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync


logger = logging.getLogger(__name__)


class TeamworkTimeConsumer(WebsocketConsumer):
    """Basic consumer for a teamwork time puzzle.

    Every user session gets an instance of this object in the backend to manage
    websocket stuff. It is short-lived and should be assumed to die shortly
    after the user disconnects; any important stuff should be persisted to the
    database.
    """

    def setup(self, puzzle_id):
        ## puzzle_id is a unique puzzle identifier tba
        self.puzzle_id = puzzle_id
        ## group is a channel group ID; it should only be truthy after
        ## successful auth
        self.group = None

    def connect(self):
        self.setup()
        self.accept()

    def disconnect(self, close_code):
        if self.group:
            async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)
        self.disconnected()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['type']
        if action == 'AUTH':
            try:
                self.team = Team.objects.get(y2021teamdata__auth=text_data_json['data'])
            except Team.DoesNotExist as e:
                logger.info(
                        f'Someone has attempted to access teamwork puzzle {self.puzzle_id}'
                        f' with invalid token {text_data_json["data"]}.')
                raise
            except Exception as e:
                logger.warn(f'Auth data {text_data} resulted in unexpected error {str(e)}.')
                raise
            self.join_or_create_session()
            self.authed()
        else:
            self.handle(text_data_json)

    def respond(self, msg):
        """Send a thing to the web client associated with this consumer."""
        self.send(text_data=json.dumps(msg))

    def channel_receive_broadcast(self, event):
        """Send a thing, which was received from a broadcast, to the web client
        associated with this consumer."""
        # Please note this default behavior when thinking about the flow of
        # your consumer! Events emitted through broadcast() have their .data
        # *passed directly to the web client for processing*! In particular,
        # this means you may need to html.escape() sometimes to prevent XSS.
        self.send(text_data=json.dumps(event['data']))

    def broadcast(self, msg):
        async_to_sync(self.channel_layer.group_send)(
                self.group, {'type': 'channel.receive_broadcast', 'data': msg})

    def authed(self):
        # Child classes should override this method to trigger action upon
        # successful authentication, instead of overriding receive().
        pass

    def disconnected(self):
        # Child classes should override this method to trigger action upon
        # disconnect, instead of overriding disconnect().
        pass

    ## Session management

    @transaction.atomic
    def join_or_create_session(self):
        session = self.get_or_create_session(self.team)
        if not session.websocket_group:
            session.websocket_group = self.generate_group_name()
            session.save()
        self.group = session.websocket_group
        async_to_sync(self.channel_layer.group_add)(self.group, self.channel_name)

    def generate_group_name(self):
        return str(uuid.uuid4())

    @transaction.atomic
    def get_or_create_session(self, team: Team):
        puzzle = Puzzle.objects.get(y2021puzzledata__tempest_id=self.puzzle_id)
        self.puzzle = puzzle
        access = PuzzleAccess.objects.get(team=team, puzzle=puzzle)
        if not access.found:
            logging.info(f'{team.username} attempted to access {puzzle.name} without unlocking it.')
            raise AccessDeniedException

        session_query_predicate = {'team': team, 'puzzle': puzzle, 'active': True}
        try:
            session, _ = TeamworkSession.objects.get_or_create(**session_query_predicate)
        except TeamworkSession.MultipleObjectsReturned:
            old_sessions = TeamworkSession.objects.select_for_update().filter(
                    **session_query_predicate).order_by('-last_update')
            with transaction.atomic():
                for old_session in old_sessions[1:]:
                    old_session.active = False
                    old_session.save()
            session, _ = TeamworkSession.objects.get_or_create(**session_query_predicate)
        return session

    @transaction.atomic
    def get_session(self):
        if self.group:
            return TeamworkSession.objects.get(websocket_group=self.group)
        else:
            return None

    def end_session(self):
        if not self.group:
            return
        session = self.get_session()
        with transaction.atomic():
            logging.info(f'Ending {session.puzzle.name} session'
                         f' for team {session.team.username}.')
            session.active = False
            session.save()

class AsyncTeamworkTimeConsumer(AsyncWebsocketConsumer):
    """Basic consumer for a teamwork time puzzle.

    Every user session gets an instance of this object in the backend to manage
    websocket stuff. It is short-lived and should be assumed to die shortly
    after the user disconnects; any important stuff should be persisted to the
    database.
    """

    def setup(self, puzzle_id):
        ## puzzle_id is a unique puzzle identifier tba
        self.puzzle_id = puzzle_id
        ## group is a channel group ID; it should only be truthy after
        ## successful auth
        self.group = None

    async def connect(self):
        self.setup()
        await self.accept()

    async def disconnect(self, close_code):
        if self.group:
            await self.channel_layer.group_discard(self.group, self.channel_name)
        self.disconnected()

    def get_team(self, auth):
        try:
            return Team.objects.get(y2021teamdata__auth=auth)
        except Team.DoesNotExist as e:
            logger.info(
                f'Someone has attempted to access teamwork puzzle {self.puzzle_id}'
                f' with invalid token {auth}.')
            raise
        except Exception as e:
            logger.warn(f'Auth data {auth} resulted in unexpected error {str(e)}.')
            raise

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['type']
        if action == 'AUTH':
            self.team = await database_sync_to_async(self.get_team)(text_data_json['data'])
            await self.join_or_create_session()
            await self.authed()
        else:
            await self.handle(text_data_json)

    async def respond(self, msg):
        """Send a thing to the web client associated with this consumer."""
        await self.send(text_data=json.dumps(msg))

    async def channel_receive_broadcast(self, event):
        """Send a thing, which was received from a broadcast, to the web client
        associated with this consumer."""
        # Please note this default behavior when thinking about the flow of
        # your consumer! Events emitted through broadcast() have their .data
        # *passed directly to the web client for processing*! In particular,
        # this means you may need to html.escape() sometimes to prevent XSS.
        await self.send(text_data=json.dumps(event['data']))

    async def broadcast(self, msg):
        await self.channel_layer.group_send(
            self.group, {'type': 'channel.receive_broadcast', 'data': msg})

    async def authed(self):
        # Child classes should override this method to trigger action upon
        # successful authentication, instead of overriding receive().
        pass

    async def disconnected(self):
        # Child classes should override this method to trigger action upon
        # disconnect, instead of overriding disconnect().
        pass

    ## Session management

    def join_or_create_session_sync(self):
        session = self.get_or_create_session(self.team)
        if not session.websocket_group:
            session.websocket_group = self.generate_group_name()
            session.save()
        self.group = session.websocket_group

    async def join_or_create_session(self):
        await database_sync_to_async(self.join_or_create_session_sync)()
        await self.channel_layer.group_add(self.group, self.channel_name)

    def generate_group_name(self):
        return str(uuid.uuid4())

    @transaction.atomic
    def get_or_create_session(self, team: Team):
        puzzle = Puzzle.objects.get(y2021puzzledata__tempest_id=self.puzzle_id)
        self.puzzle = puzzle
        access = PuzzleAccess.objects.get(team=team, puzzle=puzzle)
        if not access.found:
            logging.info(f'{team.username} attempted to access {puzzle.name} without unlocking it.')
            raise AccessDeniedException

        session_query_predicate = {'team': team, 'puzzle': puzzle, 'active': True}
        try:
            session, _ = TeamworkSession.objects.get_or_create(**session_query_predicate)
        except TeamworkSession.MultipleObjectsReturned:
            old_sessions = TeamworkSession.objects.select_for_update().filter(
                    **session_query_predicate).order_by('-last_update')
            with transaction.atomic():
                for old_session in old_sessions[1:]:
                    old_session.active = False
                    old_session.save()
            session, _ = TeamworkSession.objects.get_or_create(**session_query_predicate)
        return session

    @transaction.atomic
    def get_session(self):
        if self.group:
            return TeamworkSession.objects.get(websocket_group=self.group)
        else:
            return None

    def end_session(self):
        if not self.group:
            return
        session = self.get_session()
        with transaction.atomic():
            logging.info(f'Ending {session.puzzle.name} session'
                         f' for team {session.team.username}.')
            session.active = False
            session.save()


class TeamworkTimeWithLeaderConsumer(TeamworkTimeConsumer):
    """Teamwork time session with leader management to own singleton actions."""

    LEADER_RETRY_INTERVAL = 0.1

    # True iff this consumer is the leader
    leader = False

    @transaction.atomic
    def join_or_create_session(self):
        super(TeamworkTimeWithLeaderConsumer, self).join_or_create_session()
        self.claim_leader_maybe()

    def claim_leader_maybe(self, force=True):
        """Claim leadership of the session if one doesn't exist.

        Returns True if this consumer is the leader.
        """
        while True:
            session = self.get_session()
            with transaction.atomic():
                if bool(session.leader):
                    break
                session.leader = self.channel_name
                session.save()
            time.sleep(self.LEADER_RETRY_INTERVAL)
        self.leader = (session.leader == self.channel_name)

    def replace_leader(self):
        """Force leader repick."""
        session = self.get_session()
        with transaction.atomic():
            session.leader = ''
            session.save()
        async_to_sync(self.channel_layer.group_send)(
                self.group, {
                        'type': 'teamwork.repick_leader',
                        'sender': self.channel_name,
                })

    def teamwork_repick_leader(self, event):
        while self.get_session().leader == event['sender']:
            time.sleep(self.LEADER_RETRY_INTERVAL)
        return self.claim_leader_maybe()

    def disconnected(self):
        if self.leader:
            # This works even after super.disconnect() because you can send
            # messages to a channel group without being a member of that group
            self.replace_leader()


class AccessDeniedException(Exception):
    pass
