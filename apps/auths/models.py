# Python modules
from typing import Any
# Django modules
from django.db.models import (
    EmailField,
    CharField,
    DateTimeField,
    BooleanField,
)
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


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
    EMAIL_MAX_LENGHT = 150
    USERNAME_MAX_LENGHT = 150
    

    email = EmailField(max_length=EMAIL_MAX_LENGHT, unique=True)
    username = CharField(max_length=USERNAME_MAX_LENGHT)
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





