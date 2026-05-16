# Python Modules
from typing import Any, Optional

# Django Modules
from django.db.models import QuerySet, Count, Q
from django.utils.text import slugify
import uuid
from django.utils.translation import gettext_lazy as _

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
    CommunityMembershipSerilizer,
    CommunityNotFoundSerializer,
    CommunityResponseSerializer,
    AlreadyMemberSerializer,
    LeaveSuccessSerializer,
    OwnerCannotLeaveSerializer,
    NotMemberSerializer,
)

# Swagger modules
from drf_spectacular.utils import extend_schema, OpenApiResponse


class CommunityViewSet(ViewSet):
    """ViewSet for handling community related endpoints"""

    @extend_schema(
        summary="Retrieve a single post by ID",
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Successfully returns the requested community",
                response=CommunitySerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Event with this ID does not exist",
                response=CommunityNotFoundSerializer,
            )
        }
    )
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
            return DRFResponse({'detail': _("Community not Found")}, status=HTTP_404_NOT_FOUND)

        serializer: CommunitySerializer = CommunitySerializer(
            community, context={'request': request})
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    def get_queryset(self) -> QuerySet[Community]:
        """Get queryset with owner, memberships and annotations"""
        return (
            Community.objects
            .filter(deleted_at__isnull=True)
            .select_related('owner')
            .prefetch_related('memberships', 'posts')
            .annotate(
                active_members_count=Count(
                    'memberships', filter=Q(memberships__status='active'), distinct=True),
                posts_count=Count(
                    'posts', filter=Q(posts__deleted_at__isnull=True), distinct=True))
        )

    @extend_schema(
        summary="List all communities",
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Returns list of top-level communities",
                response=CommunitySerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Event with this ID does not exist",
                response=CommunityNotFoundSerializer,
            )
        }
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

    @extend_schema(
        summary="Create a Community",
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Community successfully created",
                response=CommunitySerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Event with this ID does not exist",
                response=CommunityNotFoundSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid data",
                response=CommunityResponseSerializer,
            ),
        }
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

    @extend_schema(
        summary="Partially update a community",
        request=CommunitySerializer,
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Community successfully updated",
                response=CommunitySerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid data",
                response=CommunityResponseSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Community with this ID does not exist",
                response=CommunityNotFoundSerializer,
            ),
        }
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
                {'detail': _("This community does not exist")},
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

    @extend_schema(
        summary="Delete a community",
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(
                description="Community successfully deleted"
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Community with this ID does not exist",
                response=CommunityNotFoundSerializer,
            ),
        }
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
                {'detail': _("Community does not exist")},
                status=HTTP_404_NOT_FOUND,
            )

        community.delete()
        return DRFResponse(
            status=HTTP_204_NO_CONTENT,
        )

    @extend_schema(
        summary="Join a community",
        request=None,
        responses={
            HTTP_201_CREATED: OpenApiResponse(
                description="Successfully joined the community",
                response=CommunityMembershipSerilizer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="User is already a member or is the owner",
                response=AlreadyMemberSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Community with this ID does not exist",
                response=CommunityNotFoundSerializer,
            ),
        }
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
                {'detail': _("Community does not exist")},
                status=HTTP_404_NOT_FOUND
            )

        existing_memberships: Optional[CommunityMembership] = CommunityMembership.objects.filter(
            user=request.user,
            community=community,
        ).first()

        if existing_memberships:
            return DRFResponse(
                {'detail': _("You are already a member of this community")},
                status=HTTP_400_BAD_REQUEST
            )

        if community.owner == request.user:
            return DRFResponse(
                {'detail': _("You are the owner of this community")},
                status=HTTP_400_BAD_REQUEST
            )

        if community.visibility == 'public':
            status = 'active'
        else:
            status = 'pending'

        membership: CommunityMembership = CommunityMembership.objects.create(
            user=request.user,
            community=community,
            role='member',
            status=status,
        )

        serilizer: CommunityMembershipSerilizer = CommunityMembershipSerilizer(
            membership)

        return DRFResponse(
            data=serilizer.data,
            status=HTTP_201_CREATED
        )

    @extend_schema(
        summary="Get all members of a community",
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Returns list of active members",
                response=CommunityMembershipSerilizer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Community with this ID does not exist",
                response=CommunityNotFoundSerializer,
            ),
        }
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
                {'detail': _("Community does not exist")},
                status=HTTP_404_NOT_FOUND
            )
        memberships: QuerySet[CommunityMembership] = CommunityMembership.objects.filter(
            community=community,
            status='active'
        ).select_related('user').order_by('joined_at')

        membership_serializer: CommunityMembershipSerilizer = CommunityMembershipSerilizer(
            memberships, many=True)
        members_list = list(membership_serializer.data)

        owner_in_members = any(m['user'] == str(
            community.owner.id) for m in members_list)
        if not owner_in_members:
            owner_memberships_data = {
                'id': str(community.owner.id),
                'user': str(community.owner.id),
                'user_username': community.owner.username,
                'community': str(community.id),
                'community_name': community.name,
                'role': 'organizer',
                'status': 'active',
                'joined_at': community.created_at.isoformat() if hasattr(community, 'created_at') and community.created_at else None,
            }
            members_list.insert(0, owner_memberships_data)

        return DRFResponse(
            data=members_list,
            status=HTTP_200_OK
        )

    @extend_schema(
        summary="Leave a community",
        request=None,
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Successfully left the community",
                response=LeaveSuccessSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Owner cannot leave their own community",
                response=OwnerCannotLeaveSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Community does not exist or user is not a member",
                response=NotMemberSerializer,
            ),
        }
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
                {'detail': _("Community does not exist")},
                status=HTTP_404_NOT_FOUND
            )

        if community.owner == request.user:
            return DRFResponse(
                {'detail': _("Owner can not leave the community")},
                status=HTTP_400_BAD_REQUEST
            )

        try:
            membership: CommunityMembership = CommunityMembership.objects.get(
                user=request.user,
                community=community
            )
            membership.delete()
            return DRFResponse(
                {'detail': _("Successfully left the community")},
                status=HTTP_200_OK
            )
        except CommunityMembership.DoesNotExist:
            return DRFResponse(
                {'detail': _("Community with this member does not exist")},
                status=HTTP_404_NOT_FOUND
            )
