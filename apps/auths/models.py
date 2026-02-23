# Python modules
from typing import Any

# Django modules
from django.db.models import (
    EmailField,
    CharField,
    DateTimeField,
    BooleanField,
    OneToOneField,
    CASCADE,
    TextField,
    JSONField,
    Model, ForeignKey, UUIDField, SET_NULL,
)
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

# Project Modules
from apps.abstracts.models import Abstract


class CustomUserManager(BaseUserManager):
    """
    Custom user manager
    """

    def __obtain_user_instance(
        self,
        email: str,
        username: str,
        password: str,
        **kwargs: dict[str, Any],
    ):
        if not email:
            raise ValidationError(message="Email field is required")
        new_user: "CustomUser" = self.model(
            email=self.normalize_email(email),
            username=username,
            password=password,
            **kwargs,
        )
        return new_user
    
    def create_user(
        self,
        email: str,
        username: str,
        password: str,
        **kwargs: dict[str, Any],
    ):
        new_user=self.__obtain_user_instance(
            email=email,
            username=username,
            password=password,
            **kwargs,
        )
        new_user.set_password(password)
        new_user.save(using=self._db)
        return new_user
    

    def create_superuser(
        self,
        email: str,
        username: str,
        password: str,
        **kwargs: dict[str, Any],
    ):
        new_superuser=self.__obtain_user_instance(
            email=email,
            username=username,
            password=password,
            **{
                "is_staff": True,
                "is_superuser": True,
                **kwargs
            },
        )
        new_superuser.set_password(password)
        new_superuser.save(using=self._db)
        return new_superuser
    

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom authentication user model
    """
    EMAIL_MAX_LENGTH = 150
    USERNAME_MAX_LENGTH = 150
    

    email = EmailField(max_length=EMAIL_MAX_LENGTH, unique=True)
    username = CharField(max_length=USERNAME_MAX_LENGTH, unique=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects: CustomUserManager = CustomUserManager()

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return f"{self.email}"


class Profile(Abstract):
    DISPLAY_MAX_LENGTH=255
    user = OneToOneField(
        CustomUser,
        on_delete=CASCADE,
        related_name='profile',
    )
    display_name = CharField(
        max_length=DISPLAY_MAX_LENGTH,
        blank=True,
    )
    bio = TextField(
        blank=True,
    )
    interests = JSONField(
        blank=True,
        null=True,
    )
    is_verified = BooleanField(
        default=False,
    )

    def __str__(self):
        return self.display_name


class UserBlock(Model):

    REASON_MAX_LENGTH=255

    blocker = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name='blocked_users'
    )

    blocked = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name="blocked_by_users"
    )

    reason = CharField(
        max_length=REASON_MAX_LENGTH,
        blank=True,
    )

    blocked_at = DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = ("blocked", "blocker")


class ActivityLog(Abstract):
    ACTION_TYPES = [
        ("login", "Login"),
        ("logout", "Logout"),
        ("post_create", "Post Created"),
        ("post_delete", "Post Deleted"),
        ("comment_create", "Commet Created"),
        ("password_change", "Password Changed"),
    ]
    USER_AGENT_MAX_LENGTH = 255
    ACTION_TYPE_MAX_LENGTH=50

    user = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name="activities",
    )

    details = TextField(
        blank=True,
    )

    user_agent = CharField(
        max_length=USER_AGENT_MAX_LENGTH,
        blank=True,
    )

    action_type = CharField(
        max_length=ACTION_TYPE_MAX_LENGTH,
        choices=ACTION_TYPES,
    )


class Report(Model):

    CONTENT_MAX_LENGTH = 50
    STATUS_MAX_LENGTH = 20
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewed", "Reviewed"),
        ("rejected", "Rejected"),
        ("resolved", "Resolved"),
    ]

    reporter = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name="reports"
    )

    content_type = CharField(
        max_length=CONTENT_MAX_LENGTH,
    )

    object_type = UUIDField()

    reason = TextField()

    status = CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default="pending"
    )

    handled_by = ForeignKey(
        CustomUser,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="handled_reports"
    )

    created_at = DateTimeField(
        auto_now_add=True,
    )











