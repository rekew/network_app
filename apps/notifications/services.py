import re
from typing import Set

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model

from apps.notifications.models import Notification
from apps.posts.models import Comment
from apps.posts.serializers import CommentSerializer
from apps.auths.models import Report


MENTION_PATTERN = re.compile(r"@(?P<username>[A-Za-z0-9_]+)")


def _get_mentioned_usernames(content: str) -> Set[str]:
    if not content:
        return set()
    return {match.group("username") for match in MENTION_PATTERN.finditer(content)}


def _send_group_event(group_name: str, event: dict) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(group_name, event)


def _serialize_notification(notification: Notification) -> dict:
    return {
        "id": notification.id,
        "sender": notification.sender_id,
        "user": notification.user_id,
        "content": notification.content,
        "is_read": notification.is_read,
        "content_type": notification.content_type,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }


def _serialize_report(report: Report) -> dict:
    return {
        "id": report.id,
        "reporter": report.reporter_id,
        "content_type": report.content_type,
        "object_type": str(report.object_type),
        "reason": report.reason,
        "status": report.status,
        "handled_by": report.handled_by_id,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


def _serialize_comment(comment: Comment) -> dict:
    serializer = CommentSerializer(comment)
    comment_data = serializer.data
    comment_data["id"] = comment.id
    return comment_data


def dispatch_post_comment_event(comment: Comment, action: str) -> None:
    _send_group_event(
        f"post.{comment.post_id}.comments",
        {
            "type": "send_comment",
            "data": {
                "action": action,
                "comment": _serialize_comment(comment),
            },
        },
    )


def dispatch_post_typing_event(post_id: int, user, status: str) -> None:
    _send_group_event(
        f"post.{post_id}.typing",
        {
            "type": "send_typing",
            "data": {
                "post_id": post_id,
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
                "status": status,
            },
        },
    )


def _create_notification(sender, recipient, content: str, content_type: str | None = None) -> Notification:
    notification = Notification.objects.create(
        sender=sender,
        user=recipient,
        content=content,
        content_type=content_type,
    )
    _send_group_event(
        f"user.{recipient.id}.notifications",
        {
            "type": "send_notification",
            "data": _serialize_notification(notification),
        },
    )
    return notification


def dispatch_comment_notifications(comment: Comment) -> None:
    if comment.parent_comment and comment.parent_comment.author_id != comment.author_id:
        _create_notification(
            sender=comment.author,
            recipient=comment.parent_comment.author,
            content=f"{comment.author.username} replied to your comment.",
            content_type="comment_reply",
        )

    mentioned_usernames = _get_mentioned_usernames(comment.content)
    if not mentioned_usernames:
        return

    User = get_user_model()
    mention_recipients = User.objects.filter(username__in=mentioned_usernames).exclude(
        id=comment.author_id
    )
    parent_author_id = comment.parent_comment.author_id if comment.parent_comment else None
    mention_recipients = mention_recipients.exclude(id=parent_author_id) if parent_author_id else mention_recipients

    for user in mention_recipients.distinct():
        _create_notification(
            sender=comment.author,
            recipient=user,
            content=f"{comment.author.username} mentioned you in a comment.",
            content_type="comment_mention",
        )


def dispatch_moderation_report(report: Report) -> None:
    _send_group_event(
        "moderation.comments",
        {
            "type": "send_report",
            "data": _serialize_report(report),
        },
    )
