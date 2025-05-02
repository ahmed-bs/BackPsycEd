from django.db import models

class TemplateCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'template_category'

class TemplateDomain(models.Model):
    template_category = models.ForeignKey(TemplateCategory, on_delete=models.CASCADE, related_name='domains')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=10, blank=True, null=True)  # To store Niveau 1, Niveau 2, etc.

    def __str__(self):
        return f"{self.name} (Category: {self.template_category})"

    class Meta:
        db_table = 'template_domain'

class TemplateItem(models.Model):
    CODE_CHOICES = [
        ('A', 'Acquis'),
        ('P', 'Partiel'),
        ('N', 'Non Acquis'),
        ('X', 'Non Coté'),
    ]

    template_domain = models.ForeignKey(TemplateDomain, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=1, choices=CODE_CHOICES, default='X', blank=True)

    def __str__(self):
        return f"{self.name} (Domain: {self.template_domain})"

    class Meta:
        db_table = 'template_item'

