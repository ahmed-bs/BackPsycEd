from django.db import models
from profiles.models import Profile
from authentification.models import CustomUser

class Strategy(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='strategies')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='authored_strategies')

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, default='Actif')
    responsible = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Strategies"
        ordering = ['-created_at']

    def __str__(self):
        return f"Strategy for {self.profile.first_name} {self.profile.last_name}: {self.title} by {self.author.username}"
