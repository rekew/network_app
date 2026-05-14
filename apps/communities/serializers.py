# Python Modules
from typing import Any, Optional

# Django Rest Framework
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    ReadOnlyField,

)
# Project Modules
from .models import Community, CommunityMembership

class CommunitySerializer(ModelSerializer):
    """Serializer for Community model"""
    owner: SerializerMethodField = SerializerMethodField()
    owner_username:ReadOnlyField = ReadOnlyField(source="owner.username")
    is_owner: SerializerMethodField = SerializerMethodField()
    is_member: SerializerMethodField = SerializerMethodField()
    membership_role: SerializerMethodField = SerializerMethodField()
    membership_status: SerializerMethodField = SerializerMethodField()
    posts_count: SerializerMethodField = SerializerMethodField()
    members_count: SerializerMethodField = SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            'id',
            'name',
            'description',
            'visibility',
            'owner',
            'owner_username',
            'created_at',
            'is_owner',
            'is_member',
            'membership_role',
            'membership_status',
            'posts_count',
            'members_count',
            'slug',
        ]

    def get_is_owner(self, obj: Community) -> bool:
        """Checking if current user is owner or not"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.owner == request.user
        return False


    def get_is_member(self, obj: Community) -> bool:
        """Check if current member is active user of the community"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.memberships.filter(user=request.user, status='active')
        return False


    def get_membership_role(self, obj: Community) -> Optional[str]:
        """Get current users' role in community"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = obj.memberships.filter(user=request.user).first()
            if membership:
                return membership.role
        return None


    def get_membership_status(self, obj: Community) -> Optional[str]:
        """Defining the users' status"""
        request=self.context.get('request')
        if request and request.user.is_authenticated:
            membership = obj.memberships.filter(user=request.user).first()
            if membership:
                return membership.status
        return None


    def get_posts_count(self, obj: Community) -> int:
        """Получить общее количество постов"""
        if hasattr(obj, 'posts_count') and not callable(obj.posts_count):
            return obj.posts_count
        
        try:
            return obj.posts.count() 
        except AttributeError:
            return 0


    def get_members_count(self, obj: Community) -> int:
        """Get total numbers of members"""
        if hasattr(obj, 'active_members_count'):
            return 1 + (obj.active_members_count or 0)
        active_members = obj.memberships.filter(status='active').count()
        return 1 + active_members


    def get_owner(self, obj: Community) -> str:
        """Get owner id as string"""
        return str(obj.owner.id)


class CommunityMembershipSerilizer(ModelSerializer):
    """Serializer for Community Membership"""
    user_username: ReadOnlyField = ReadOnlyField(source='user.username')
    community_name: ReadOnlyField = ReadOnlyField(source='community.name')

    class Meta:
        model = CommunityMembership
        fields = [
            'id',
            'user',
            'user_username',
            'community',
            'community_name',
            'role',
            'status',
            'joined_at',
        ]