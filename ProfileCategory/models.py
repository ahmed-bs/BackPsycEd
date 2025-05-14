from django.db import models
from ProfileItem.models import ProfileItem
from profiles.models import Profile

# profile_data/models.py
class ProfileCategory(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def domains_count(self):
        return self.profiledomain_set.count()

    @property
    def items_count(self):
        return ProfileItem.objects.filter(profile_domain__profile_category=self).count()
