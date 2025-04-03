from django.db import models

class TermdeCondition(models.Model):
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Termes et Conditions - {self.date_creation}"