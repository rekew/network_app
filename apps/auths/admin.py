# Django modules
from django.contrib.admin import register, ModelAdmin

# Project modules
from apps.auths.models import CustomUser


@register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    """
    Admin class for Customuser
    """

    list_display = [
        "id",
        "email",
        "username",
        "created_at",
        "updated_at",
    ]
    list_filter = ["id", "email", "username"]
    search_field = ["id", "email", "username"]
    readonly_fields = ["created_at"]
    list_per_page = 30

