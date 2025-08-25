from django.db import models

# Create your models here.
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ProfileDomain.models import ProfileDomain


class ProfileItem(models.Model):
    ETAT_CHOICES = [
        ('ACQUIS', 'Acquis'),
        ('PARTIEL', 'Partiel'),
        ('NON_ACQUIS', 'Non Acquis'),
        ('NON_COTE', 'Non Coté'),
    ]

    profile_domain = models.ForeignKey(ProfileDomain, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=500)
    name_ar = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    description_ar = models.TextField(blank=True, null=True)
    commentaire = models.TextField(blank=True, null=True)
    commentaire_ar = models.TextField(blank=True, null=True)
    is_modified = models.BooleanField(default=False)
    modified_at = models.DateTimeField(auto_now=True)
    etat = models.CharField(max_length=10, choices=ETAT_CHOICES, default='NON_COTE')

    def __str__(self):
        return f"{self.name} (Domain: {self.profile_domain})"

    class Meta:
        db_table = 'profile_item'

# Signals to update ProfileDomain metrics
@receiver([post_save, post_delete], sender=ProfileItem)
def update_domain_metrics(sender, instance, **kwargs):
    """Update item_count and acquis_percentage when a ProfileItem is saved or deleted."""
    instance.profile_domain.update_metrics()