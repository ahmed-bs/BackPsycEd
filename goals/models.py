from django.db import models
from django.conf import settings
from ProfileDomain.models import ProfileDomain
from profiles.models import Profile

class Goal(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='goals') # Removed null=True, blank=True
    domain = models.ForeignKey(
        ProfileDomain,
        on_delete=models.SET_NULL,
        related_name='goals',
        null=True,
        blank=True 
    )
    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    description_ar = models.TextField(blank=True, null=True)
    target_date = models.DateField()
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ],
        default='medium'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Goal for {self.profile.first_name} {self.profile.last_name}: {self.title}"

    class Meta:
        ordering = ['-created_at']

class SubObjective(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='sub_objectives')
    description = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ['created_at']