# questions/models.py
from django.db import models
from goals.models import Goal

class Question(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return self.text