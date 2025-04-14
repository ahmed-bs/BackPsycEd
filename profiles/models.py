from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from authentification.models import CustomUser
from categories.models import UserCategory
class Profile(models.Model):
    parent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='children')
    category = models.ForeignKey(UserCategory, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    diagnosis = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    bio = models.BinaryField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"  # Fixed the __str__ method


class ProfileShare(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='shared_profiles')
    shared_with = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='shared_with_me')
    can_read = models.BooleanField(default=False)
    can_write = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("can_read_shared_profile", "Can read shared profile"),
            ("can_write_shared_profile", "Can write shared profile"),
            ("can_update_shared_profile", "Can update shared profile"),
            ("can_delete_shared_profile", "Can delete shared profile"),
        ]

    def __str__(self):
        return f"{self.profile.user.username} shared with {self.shared_with.user.username}"
