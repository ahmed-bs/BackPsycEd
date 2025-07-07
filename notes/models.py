from django.db import models
from django.conf import settings

class Note(models.Model):
    """
    Represents a user's note or observation.
    Each note is associated with a specific user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name="User"
    )
    content = models.TextField(
        verbose_name="Note Content"
    )
    is_important = models.BooleanField(
        default=False,
        verbose_name="Is Important Note"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated At"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Note"
        verbose_name_plural = "Notes"

    def __str__(self):
        return f"Note by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"