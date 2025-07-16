from django.db import models
from django.conf import settings
from profiles.models import Profile

class Note(models.Model):
    """
    Represents a note or observation.
    Each note is associated with a specific profile.
    Each note also tracks the user who created it (the author).
    """
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="profile_notes",
        verbose_name="Profile"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_notes',
        verbose_name="Author"
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
        return f"Note by {self.author.username} for {self.profile.first_name} {self.profile.last_name}: {self.content[:30]}..."