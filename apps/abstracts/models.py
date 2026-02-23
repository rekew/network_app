# Django Modules
from django.db.models import Model, DateTimeField

class Abstract(Model):
    """
    Abstract Base Model for users
    """

    created_at=DateTimeField(
        auto_now_add=True
    )
    updated_at=DateTimeField(
        auto_now=True
    )
    deleted_at=DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        abstract=True