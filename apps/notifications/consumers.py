from channels.generic.websocket import AsyncWebsocketConsumer
import json


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f'user.{self.user.id}.notifications'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event['data']))


class PostCommentsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.group_name = f'post.{self.post_id}.comments'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_comment(self, event):
        await self.send(text_data=json.dumps(event['data']))


class PostTypingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.group_name = f'post.{self.post_id}.typing'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            return

        action = payload.get('action')
        if action not in ('start', 'stop'):
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_typing',
                'data': {
                    'post_id': self.post_id,
                    'user': {
                        'id': self.user.id,
                        'username': self.user.username,
                    },
                    'status': action,
                },
            },
        )

    async def send_typing(self, event):
        await self.send(text_data=json.dumps(event['data']))


class ModerationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated or not self.user.is_staff:
            await self.close(code=4001)
            return

        self.group_name = 'moderation.comments'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_report(self, event):
        await self.send(text_data=json.dumps(event['data']))