# goals/models.py
from django.db import models

class Goal(models.Model):
    objective_text = models.TextField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    achieved = models.BooleanField(default=False)

    def __str__(self):
        return self.name
