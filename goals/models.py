from django.db import models
from django.conf import settings
from ProfileDomain.models import ProfileDomain
from authentification.models import CustomUser

class Goal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='goals')
    domain = models.ForeignKey(
        ProfileDomain,
        on_delete=models.SET_NULL,
        related_name='goals',
        null=True,
        blank=True 
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
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
        return self.title

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