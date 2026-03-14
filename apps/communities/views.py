# Python Modules
from typing import Any, Optional

# Django Modules
from django.db.models import QuerySet, Count, Q
from django.utils.text import slugify
import uuid

# Django Rest Framework
from rest_framework.viewsets import ViewSet
from rest_framework.status import (
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse

# Project Modules
from .models import Community, CommunityMembership
from .serializers import (
    CommunitySerializer,
    CommunityMembershipSerilizer
)


class CommunityViewSet(ViewSet):
    """ViewSet for handling community related endpoints"""

    
    def retrieve(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get Community"""
        try:
            community = self.get_queryset().get(id=kwargs['pk'])
        except Community.DoesNotExist:
            return DRFResponse({'detail': 'COmmunity not Found'}, status=HTTP_404_NOT_FOUND)

        serializer:CommunitySerializer= CommunitySerializer(community, context={'request':request})
        return DRFResponse(serializer.data, status=HTTP_200_OK)


    def get_queryset(self) -> QuerySet[Community]:
        """Get queryset with owner, memberships and annotations"""
        return(
            Community.objects
            .filter(deleted_at__isnull=True)
            .select_related('owner')
            .prefetch_related('memberships', 'posts')
            .annotate(
                active_members_count=Count('memberships', filter=Q(memberships__status='active'), distinct=True),
                posts_count=Count('posts', filter=Q(posts__deleted_at__isnull=True), distinct=True)
            )
        )


    def list(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Get all list of communities"""
        queryset = self.get_queryset()

        # filterset = self.filterset_class(request.query_params, queryset=queryset)
        # if filterset.is_valid():
        #     queryset = filterset.qs

        ordering = request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(*ordering.split(','))

        serilizer: CommunitySerializer = CommunitySerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return DRFResponse(
            data=serilizer.data,
            status=HTTP_200_OK
        )
    

    def create(self, request, *args, **kwargs):
        """Create a new Community"""
        data = request.data.copy()
        base_slug = slugify(data.get('name', ''))
        if not base_slug:
            base_slug = 'community'
    
        slug = base_slug
        
        while Community.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
    
        data['slug'] = slug
    
        serializer = CommunitySerializer(
            data=data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return DRFResponse(
                data=serializer.errors, 
                status=HTTP_400_BAD_REQUEST
            )
        
        serializer.save(owner=request.user)
        return DRFResponse(
            data=serializer.data, 
            status=HTTP_201_CREATED
        )


    def partial_update(self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Partially update the community"""

        try:
            community: Community = self.get_queryset().get(id=kwargs['pk'])
        except Community.DoesNotExist:
            return DRFResponse(
                {'detail': 'This community doe not exist'},
                status=HTTP_400_BAD_REQUEST
            )

        serializer: CommunitySerializer = CommunitySerializer(
            instance=community,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK
        )


    def destroy(self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Destroy the community"""
        try:
            community: Community = self.get_queryset().get(id=kwargs['pk'])
        except Community.DoesNotExist:
            return DRFResponse(
                {'detail': 'Community does not exist'},
                status=HTTP_404_NOT_FOUND,
            )

        community.delete()
        return DRFResponse(
            status=HTTP_204_NO_CONTENT,
        )


    @action(
        methods=['POST'],
        detail=True,
        url_path='join',
        permission_classes=[IsAuthenticated,]
    )
    def join(self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """ Join a company - creates membership with appropriate status"""
        try:
            community: Community = self.get_queryset().get(id=kwargs['pk'])
        except Community.DoesNotExist:
            return DRFResponse(
                {'detail': 'Community does not exist'},
                status=HTTP_404_NOT_FOUND
            )

        existing_memberships: Optional[CommunityMembership] = CommunityMembership.objects.filter(
            user=request.user,
            community=community,
        ).first()

        if existing_memberships:
            return DRFResponse(
                {'detail': 'You are already a member of this community'},
                status=HTTP_400_BAD_REQUEST
            )

        if community.owner == request.user:
            return DRFResponse(
                {'detail': 'You are the owner of this community'},
                status=HTTP_400_BAD_REQUEST
            )

        if community.visibility == 'public':
            status = 'active'
        else:
            status = 'pending'

        membership:CommunityMembership = CommunityMembership.objects.create(
            user=request.user,
            community=community,
            role='member',
            status=status,
        )

        serilizer:CommunityMembershipSerilizer = CommunityMembershipSerilizer(membership)

        return DRFResponse(
            data=serilizer.data,
            status=HTTP_201_CREATED
        )


    @action(
        methods=['GET'],
        detail=True,
        url_path='members',
        permission_classes=[IsAuthenticated, ]
    )
    def members(self,
             request: DRFRequest,
             *args: tuple[Any, ...],
             **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """ Get all the members of the community """

        try:
            community: Community = self.get_queryset().get(id=kwargs['pk'])
        except Community.DoesNotExist:
            return DRFResponse(
                {'detail': 'Community does not exist'},
                status=HTTP_404_NOT_FOUND
            )
        memberships: QuerySet[CommunityMembership] = CommunityMembership.objects.filter(
            community=community,
            status = 'active'
        ).select_related('user').order_by('joined_at')

        membership_serializer: CommunityMembershipSerilizer = CommunityMembershipSerilizer(memberships, many=True)
        members_list = list(membership_serializer.data)

        owner_in_members = any(m['user'] == str(community.owner.id) for m in members_list)
        if not owner_in_members:
            owner_memberships_data = {
                'id': str(community.owner.id),
                'user': str(community.owner.id),
                'user_username': community.owner.username,
                'community': str(community.id),
                'community_name': community.name,
                'role': 'organizer',
                'status': 'active',
                'joined_at': community.created_at.isoformat() if hasattr(community,'created_at') and community.created_at else None,
            }
            members_list.insert(0, owner_memberships_data)

        return DRFResponse(
            data=members_list,
            status=HTTP_200_OK
        )


    @action(
        methods=['POST'],
        detail=True,
        url_path='leave',
        permission_classes=[IsAuthenticated, ]
    )
    def leave(self,
                request: DRFRequest,
                *args: tuple[Any, ...],
                **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """Leave the community"""
        try:
            community: Community = self.get_queryset().get(id=kwargs['pk'])
        except Community.DoesNotExist:
            return DRFResponse(
                {'detail': 'Community does not exist'},
                status=HTTP_404_NOT_FOUND
            )

        if community.owner == request.user:
            return DRFResponse(
                {'detail': 'Owner can not leave the community'},
                status=HTTP_400_BAD_REQUEST
            )

        try:
            membership: CommunityMembership = CommunityMembership.objects.get(
                user=request.user,
                community=community
            )
            membership.delete()
            return DRFResponse(
                {'detail': 'Successfully left the community'},
                status=HTTP_200_OK
            )
        except CommunityMembership.DoesNotExist:
            return DRFResponse(
                {'detail': 'Community with this member does not exist'},
                status=HTTP_404_NOT_FOUND
            )
