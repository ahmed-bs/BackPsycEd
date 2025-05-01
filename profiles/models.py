from django.db import models
from django.conf import settings
from authentification.models import CustomUser

GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
class Profile(models.Model):
    category = models.CharField(max_length=50, blank=True, null=True)  # Store as string
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    diagnosis = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    evaluation_score = models.IntegerField(default=0)
    objectives = models.JSONField(default=list, blank=True)
    progress = models.CharField(max_length=100, default='En progrès')
    recommended_strategies = models.JSONField(default=list, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    bio = models.BinaryField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    @property
    def associated_users(self):
        """Return all users associated with this profile via SharedProfilePermission."""
        return CustomUser.objects.filter(shared_profiles__profile=self).distinct()

class SharedProfilePermission(models.Model):
    PERMISSION_CHOICES = [
        ('view', 'View'),
        ('edit', 'Edit'),
        ('share', 'Share'),
        ('delete', 'Delete'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='shared_with')
    shared_with = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shared_profiles')
    permissions = models.CharField(max_length=10, choices=PERMISSION_CHOICES)

    class Meta:
        unique_together = ('profile', 'shared_with', 'permissions')  
    def __str__(self):
        return f"{self.shared_with.username} has {self.permissions} permission on {self.profile}"
