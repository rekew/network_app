# Python Modules
import json

# Django Modules
from django.db.models import QuerySet

# Channels Modules
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# Project Modules
from apps.posts.models import Comment, Reaction


class CommentReactionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time comment reaction updates.
    Channel: comment.<comment_id>.reactions
    """

    async def connect(self) -> None:
        self.comment_id = self.scope["url_route"]["kwargs"]["comment_id"]
        self.group_name = f"comment_{self.comment_id}_reactions"

        comment_exists = await self.get_comment()
        if not comment_exists:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )
        await self.accept()

        # Send current reaction counts on connect
        counts = await self.get_reaction_counts()
        await self.send(text_data=json.dumps({
            "type": "reaction_counts",
            "comment_id": self.comment_id,
            "reactions": counts,
        }))

    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def receive(self, text_data: str) -> None:
        
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.send(text_data=json.dumps({
                "type": "error",
                "detail": "Authentication required",
            }))
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "detail": "Invalid JSON",
            }))
            return

        action = data.get("action")
        reaction_type = data.get("reaction_type")

        valid_types = [r.value for r in Reaction.ReactionType]
        if reaction_type not in valid_types:
            await self.send(text_data=json.dumps({
                "type": "error",
                "detail": f"Invalid reaction_type. Must be one of: {valid_types}",
            }))
            return

        if action == "add":
            await self.add_reaction(user, reaction_type)
        elif action == "remove":
            await self.remove_reaction(user, reaction_type)
        else:
            await self.send(text_data=json.dumps({
                "type": "error",
                "detail": "action must be 'add' or 'remove'",
            }))
            return

        counts = await self.get_reaction_counts()
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "reaction_update",
                "comment_id": self.comment_id,
                "reactions": counts,
                "actor_id": str(user.id),
                "actor_username": user.username,
                "action": action,
                "reaction_type": reaction_type,
            }
        )


    async def reaction_update(self, event: dict) -> None:
        """Broadcast reaction update to WebSocket client"""
        await self.send(text_data=json.dumps({
            "type": "reaction_update",
            "comment_id": event["comment_id"],
            "reactions": event["reactions"],
            "actor_id": event["actor_id"],
            "actor_username": event["actor_username"],
            "action": event["action"],
            "reaction_type": event["reaction_type"],
        }))


    @database_sync_to_async
    def get_comment(self) -> bool:
        return Comment.objects.filter(id=self.comment_id).exists()

    @database_sync_to_async
    def get_reaction_counts(self) -> dict:
        counts = {}
        for reaction_type in Reaction.ReactionType:
            counts[reaction_type.value] = Reaction.objects.filter(
                comment_id=self.comment_id,
                reaction_type=reaction_type.value,
            ).count()
        return counts

    @database_sync_to_async
    def add_reaction(self, user, reaction_type: str) -> None:
        Reaction.objects.filter(
            user=user,
            comment_id=self.comment_id,
        ).delete()

        Reaction.objects.create(
            user=user,
            comment_id=self.comment_id,
            reaction_type=reaction_type,
        )

    @database_sync_to_async
    def remove_reaction(self, user, reaction_type: str) -> None:
        Reaction.objects.filter(
            user=user,
            comment_id=self.comment_id,
            reaction_type=reaction_type,
        ).delete()