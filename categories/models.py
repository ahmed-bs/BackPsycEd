from django.db import models

class Category(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100)
    created_date = models.DateField()
    items_count = models.PositiveIntegerField()
    domains_count = models.PositiveIntegerField()

    def __str__(self):
        return self.title


class Item(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class Domain(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='domains')
    items = models.ManyToManyField(Item, related_name='domains')

    def __str__(self):
        return self.title
