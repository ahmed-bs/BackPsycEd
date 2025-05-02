from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from profiles.models import Profile
from template_data.models import TemplateCategory, TemplateDomain, TemplateItem

class ProfileCategory(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='categories')
    template_category = models.ForeignKey(TemplateCategory, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} (Profile: {self.profile})"

    class Meta:
        db_table = 'profile_category'

class ProfileDomain(models.Model):
    profile_category = models.ForeignKey(ProfileCategory, on_delete=models.CASCADE, related_name='domains')
    template_domain = models.ForeignKey(TemplateDomain, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    item_count = models.PositiveIntegerField(default=0, editable=False)  # Number of items
    acquis_percentage = models.FloatField(default=0.0, editable=False)  # Percentage of Acquis items

    def __str__(self):
        return f"{self.name} (Category: {self.profile_category})"

    def update_metrics(self):
        """Update item_count and acquis_percentage."""
        items = self.items.all()
        total_items = items.count()
        acquis_items = items.filter(etat='ACQUIS').count()
        self.item_count = total_items
        self.acquis_percentage = (acquis_items / total_items * 100) if total_items > 0 else 0.0
        self.save()

    class Meta:
        db_table = 'profile_domain'

class ProfileItem(models.Model):
    ETAT_CHOICES = [
        ('ACQUIS', 'Acquis'),
        ('PARTIEL', 'Partiel'),
        ('NON_ACQUIS', 'Non Acquis'),
        ('NON_COTE', 'Non Coté'),
    ]

    profile_domain = models.ForeignKey(ProfileDomain, on_delete=models.CASCADE, related_name='items')
    template_item = models.ForeignKey(TemplateItem, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
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