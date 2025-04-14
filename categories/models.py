from django.db import models
from django.conf import settings

class AbstractCategory(models.Model):
    code = models.CharField(max_length=10)
    title = models.CharField(max_length=100)
    created_date = models.DateField()
    items_count = models.PositiveIntegerField()
    domains_count = models.PositiveIntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
    
class DefaultCategory(AbstractCategory):
    CATEGORY_AGE_CHOICES = [
        ('petit_enfant', 'Moins de 6 ans'),
        ('grand_enfant', '6 ans et plus'),
    ]
    age_type = models.CharField(max_length=20, choices=CATEGORY_AGE_CHOICES)


class UserCategory(AbstractCategory):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    
class AbstractDomain(models.Model):
    code = models.CharField(max_length=10)
    title = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
    
class DefaultDomain(AbstractDomain):
    category = models.ForeignKey(DefaultCategory, on_delete=models.CASCADE, related_name='domains')
    items = models.ManyToManyField('DefaultItem', related_name='domains')


class UserDomain(AbstractDomain):
    category = models.ForeignKey(UserCategory, on_delete=models.CASCADE, related_name='domains')
    items = models.ManyToManyField('UserItem', related_name='domains')

class AbstractItem(models.Model):
    code = models.CharField(max_length=10)
    title = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
    
class DefaultItem(AbstractItem):
    pass


class UserItem(AbstractItem):
    pass
