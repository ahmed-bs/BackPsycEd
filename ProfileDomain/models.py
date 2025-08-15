from django.db import models
from django.utils import timezone

class ProfileDomain(models.Model):
    profile_category = models.ForeignKey('ProfileCategory.ProfileCategory', on_delete=models.CASCADE, related_name='domains')
    name = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    description_ar = models.TextField(blank=True, null=True)
    item_count = models.PositiveIntegerField(default=0, editable=False)
    acquis_percentage = models.FloatField(default=0.0, editable=False)
    start_date = models.DateField(default=timezone.now)
    last_evaluation_date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Category: {self.profile_category})"

    def update_metrics(self):
        """Update item_count, acquis_percentage, and last_evaluation_date."""
        items = self.items.all()
        total_items = items.count()
        acquis_items = items.filter(etat='ACQUIS').count()
        self.item_count = total_items
        self.acquis_percentage = (acquis_items / total_items * 100) if total_items > 0 else 0.0
        self.save()

    class Meta:
        db_table = 'profile_domain'